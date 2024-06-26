#!/usr/bin/env python3.4
#
#   Copyright 2016 - The Android Open Source Project
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import time

import acts.signals as signals

from acts import asserts
from acts import base_test
from acts.controllers import android_device
from acts.controllers import attenuator
from acts.test_decorators import test_tracker_info
from acts_contrib.test_utils.wifi import wifi_test_utils as wutils
from acts_contrib.test_utils.wifi.WifiBaseTest import WifiBaseTest

WifiEnums = wutils.WifiEnums

AP_1 = 0
AP_2 = 1
# WifiNetworkSelector imposes a 10 seconds gap between two selections
NETWORK_SELECTION_TIME_GAP = 12
LVL1_ATTN = 15
LVL2_ATTN = 30
MIN_ATTN = 0
MAX_ATTN = 95
ATTN_SLEEP = 12


class WifiNetworkSelectorTest(WifiBaseTest):
    """These tests verify the behavior of the Android Wi-Fi Network Selector
    feature.
    """

    def __init__(self, configs):
        super().__init__(configs)
        self.enable_packet_log = True

    def setup_class(self):
        super().setup_class()

        self.dut = self.android_devices[0]
        wutils.wifi_test_device_init(self.dut)
        self.ap1_2g_attn = 0
        self.ap1_5g_attn = 1
        self.ap2_2g_attn = 2
        self.ap2_5g_attn = 3
        if "AccessPoint" in self.user_params:
            self.legacy_configure_ap_and_start(mirror_ap=False, ap_count=2)
        elif "OpenWrtAP" in self.user_params:
            self.configure_openwrt_ap_and_start(open_network=True,
                                                wpa_network=True,
                                                ap_count=2)
            self.ap1_5g_attn, self.ap2_2g_attn, self.ap2_5g_attn, = 0, 1, 1
        self.configure_packet_capture()

    def setup_test(self):
        super().setup_test()
        self.dut.droid.wakeLockAcquireBright()
        self.dut.droid.wakeUpNow()
        self.dut.ed.clear_all_events()
        for a in self.attenuators:
            a.set_atten(MAX_ATTN)
        time.sleep(ATTN_SLEEP)

    def teardown_test(self):
        super().teardown_test()
        for a in self.attenuators:
            a.set_atten(MIN_ATTN)
        wutils.reset_wifi(self.dut)
        self.dut.droid.wakeLockRelease()
        self.dut.droid.goToSleepNow()

    def teardown_class(self):
        if "AccessPoint" in self.user_params:
            del self.user_params["reference_networks"]
            del self.user_params["open_network"]

    """ Helper Functions """

    def add_networks(self, ad, networks):
        """Add Wi-Fi networks to an Android device and verify the networks were
        added correctly.

        Args:
            ad: the AndroidDevice object to add networks to.
            networks: a list of dicts, each dict represents a Wi-Fi network.
        """
        for network in networks:
            ret = ad.droid.wifiAddNetwork(network)
            asserts.assert_true(ret != -1,
                                "Failed to add network %s" % network)
            ad.droid.wifiEnableNetwork(ret, 0)

        configured_networks = ad.droid.wifiGetConfiguredNetworks()
        self.log.info("Configured networks: %s", configured_networks)

    def connect_and_verify_connected_bssid(self, network):
        """Start a scan to get the DUT connected to an AP and verify the DUT
        is connected to the correct BSSID.

        Args:
            expected_bssid: Network bssid to which connection.

        Returns:
            True if connection to given network happen, else return False.
        """
        expected_ssid = network['SSID']
        expected_bssid = network['bssid']
        wutils.start_wifi_connection_scan_and_ensure_network_found(
            self.dut, expected_ssid)
        time.sleep(20)
        actual_network = self.dut.droid.wifiGetConnectionInfo()
        self.log.info("Actual network: %s", actual_network)
        asserts.assert_true(
            actual_network and WifiEnums.BSSID_KEY in actual_network and \
                expected_bssid.lower() == actual_network[
                    WifiEnums.BSSID_KEY].lower(),
            "Expected BSSID: %s, Actual BSSID: %s" %
            (expected_bssid, actual_network[WifiEnums.BSSID_KEY]))
        self.log.info("DUT connected to valid network: %s" % expected_bssid)

    """ Tests Begin """

    @test_tracker_info(uuid="ffa5e278-db3f-4e17-af11-6c7a3e7c5cc2")
    def test_network_selector_automatic_connection(self):
        """
            1. Add one saved network to DUT.
            2. Move the DUT in range.
            3. Verify the DUT is connected to the network.
        """
        # add a saved network to DUT
        networks = [self.reference_networks[AP_1]['5g']]
        self.add_networks(self.dut, networks)

        # move the DUT in range
        self.attenuators[self.ap1_5g_attn].set_atten(MIN_ATTN)
        time.sleep(ATTN_SLEEP)

        # verify DUT is connected to AP_1 5g network
        network = self.reference_networks[AP_1]['5g'].copy()
        if "OpenWrtAP" in self.user_params:
            network['bssid'] = self.bssid_map[AP_1]['5g'][network["SSID"]]
        self.connect_and_verify_connected_bssid(network)

    @test_tracker_info(uuid="3ea818f2-10d7-4aad-bfab-7d8fb25aae78")
    def test_network_selector_basic_connection_prefer_5g(self):
        """
            1. Add one saved SSID with 2G and 5G BSSIDs of similar RSSI.
            2. Move the DUT in range.
            3. Verify the DUT is connected to the 5G BSSID.
        """
        # add a saved network with both 2G and 5G BSSIDs to DUT
        networks = [
            self.reference_networks[AP_1]['2g'],
            self.reference_networks[AP_1]['5g']
        ]
        self.add_networks(self.dut, networks)

        # Move DUT in range
        self.attenuators[self.ap1_2g_attn].set_atten(MIN_ATTN)
        self.attenuators[self.ap1_5g_attn].set_atten(MIN_ATTN)
        time.sleep(ATTN_SLEEP)

        # verify DUT is connected to 5G network
        network = self.reference_networks[AP_1]['5g'].copy()
        if "OpenWrtAP" in self.user_params:
            network['bssid'] = self.bssid_map[AP_1]['5g'][network["SSID"]]
        self.connect_and_verify_connected_bssid(network)

    @test_tracker_info(uuid="bebb29ca-4486-4cde-b390-c5f8f2e1580c")
    def test_network_selector_prefer_stronger_rssi(self):
        """
            1. Add two saved SSIDs to DUT, same band, one has stronger RSSI
               than the other.
            2. Move the DUT in range.
            3. Verify the DUT is connected to the SSID with stronger RSSI.
        """
        # add a 2G and a 5G saved network to DUT
        networks = [
            self.reference_networks[AP_1]['2g'],
            self.reference_networks[AP_2]['2g']
        ]
        self.add_networks(self.dut, networks)

        # move the DUT in range
        self.attenuators[self.ap1_2g_attn].set_atten(LVL1_ATTN)
        self.attenuators[self.ap2_2g_attn].set_atten(LVL2_ATTN)
        time.sleep(ATTN_SLEEP)

        # verify DUT is connected AP_1
        network = self.reference_networks[AP_1]['2g'].copy()
        if "OpenWrtAP" in self.user_params:
            network['bssid'] = self.bssid_map[AP_1]['2g'][network["SSID"]]
        self.connect_and_verify_connected_bssid(network)

    @test_tracker_info(uuid="f9f72dc5-034f-4fe2-a27d-df1b6cae76cd")
    def test_network_selector_prefer_secure_over_open_network(self):
        """
            1. Add two saved networks to DUT, same band, similar RSSI, one uses
               WPA2 security, the other is open.
            2. Move the DUT in range.
            3. Verify the DUT is connected to the secure network that uses WPA2.
        """
        # add a open network and a secure saved network to DUT
        networks = [
            self.open_network[AP_1]['5g'], self.reference_networks[AP_1]['5g']
        ]
        self.add_networks(self.dut, networks)

        # Move DUT in range
        self.attenuators[self.ap1_5g_attn].set_atten(MIN_ATTN)
        time.sleep(ATTN_SLEEP)

        # verify DUT connects to secure network
        network = self.reference_networks[AP_1]['5g'].copy()
        if "OpenWrtAP" in self.user_params:
            network['bssid'] = self.bssid_map[AP_1]['5g'][network["SSID"]]
        self.connect_and_verify_connected_bssid(network)

    @test_tracker_info(uuid="ab2c527c-0f9c-4f09-a13f-e3f461b7da52")
    def test_network_selector_blacklist_by_connection_failure(self):
        """
            1. Add two saved secured networks X and Y to DUT. X has stronger
               RSSI than Y. X has wrong password configured.
            2. Move the DUT in range.
            3. Verify the DUT is connected to network Y.
        """
        # add two saved networks to DUT, and one of them is configured with
        # incorrect password
        wrong_passwd_network = self.reference_networks[AP_1]['5g'].copy()
        wrong_passwd_network['password'] += 'haha'
        networks = [wrong_passwd_network, self.reference_networks[AP_2]['5g']]
        self.add_networks(self.dut, networks)

        # make AP_1 5G has stronger RSSI than AP_2 5G
        self.attenuators[self.ap1_5g_attn].set_atten(MIN_ATTN)
        self.attenuators[self.ap2_5g_attn].set_atten(LVL1_ATTN)
        time.sleep(ATTN_SLEEP)

        # start 3 scans to get AP_1 5G blacklisted because of the incorrect
        # password
        for _ in range(3):
            wutils.start_wifi_connection_scan_and_return_status(self.dut)
            time.sleep(NETWORK_SELECTION_TIME_GAP)

        # verify DUT is connect AP_2 5G
        network = self.reference_networks[AP_2]['5g'].copy()
        if "OpenWrtAP" in self.user_params:
            network['bssid'] = self.bssid_map[AP_2]['5g'][network["SSID"]]
        self.connect_and_verify_connected_bssid(network)

    @test_tracker_info(uuid="71d88fcf-c7b8-4fd2-a7cb-84ac4a130ecf")
    def network_selector_2g_to_5g_prefer_same_SSID(self):
        """
            1. Add SSID_A and SSID_B to DUT. Both SSIDs have both 2G and 5G
               BSSIDs.
            2. Attenuate the networks so that the DUT is connected to SSID_A's
               2G in the beginning.
            3. Increase the RSSI of both SSID_A's 5G and SSID_B's 5G.
            4. Verify the DUT switches to SSID_A's 5G.
        """
        #add two saved networks to DUT
        networks = [
            self.reference_networks[AP_1]['2g'],
            self.reference_networks[AP_2]['2g']
        ]
        self.add_networks(self.dut, networks)
        #make AP_1 2G in range
        self.attenuators[AP_1_2G_ATTENUATOR].set_atten(0)
        #verify
        self.connect_and_verify_connected_bssid(
            self.reference_networks[AP_1]['2g']['bssid'])
        #make both AP_1 and AP_2 5G in range with similar RSSI
        self.attenuators[AP_1_5G_ATTENUATOR].set_atten(0)
        self.attenuators[AP_2_5G_ATTENUATOR].set_atten(0)
        #ensure the time gap between two network selections
        time.sleep(NETWORK_SELECTION_TIME_GAP)
        #verify
        self.connect_and_verify_connected_bssid(
            self.reference_networks[AP_1]['5g']['bssid'])

    @test_tracker_info(uuid="c1243cf4-d96e-427e-869e-3d640bee3f28")
    def network_selector_2g_to_5g_different_ssid(self):
        """
            1. Add SSID_A and SSID_B to DUT. Both SSIDs have both 2G and 5G
               BSSIDs.
            2. Attenuate the networks so that the DUT is connected to SSID_A's
               2G in the beginning.
            3. Increase the RSSI of SSID_B's 5G while attenuate down SSID_A's
               2G RSSI.
            4. Verify the DUT switches to SSID_B's 5G.
        """
        # add two saved networks to DUT
        networks = [
            self.reference_networks[AP_1]['2g'],
            self.reference_networks[AP_2]['2g']
        ]
        self.add_networks(self.dut, networks)

        # make both AP_1 2G and AP_2 5G in range, and AP_1 2G
        # has much stronger RSSI than AP_2 5G
        self.attenuators[AP_1_2G_ATTENUATOR].set_atten(0)
        self.attenuators[AP_2_5G_ATTENUATOR].set_atten(20)
        #verify
        self.connect_and_verify_connected_bssid(
            self.reference_networks[AP_1]['2g']['bssid'])
        #bump up AP_2 5G RSSI and reduce AP_1 2G RSSI
        self.attenuators[AP_1_2G_ATTENUATOR].set_atten(40)
        self.attenuators[AP_2_5G_ATTENUATOR].set_atten(0)
        #ensure the time gap between two network selections
        time.sleep(NETWORK_SELECTION_TIME_GAP)
        #verify
        self.connect_and_verify_connected_bssid(
            self.reference_networks[AP_2]['5g']['bssid'])

    @test_tracker_info(uuid="10da95df-83ed-4447-89f8-735b08dbe2eb")
    def network_selector_5g_to_2g_same_ssid(self):
        """
            1. Add one SSID that has both 2G and 5G to the DUT.
            2. Attenuate down the 2G RSSI.
            3. Connect the DUT to the 5G BSSID.
            4. Bring up the 2G RSSI and attenuate down the 5G RSSI.
            5. Verify the DUT switches to the 2G BSSID.
        """
        #add a saved network to DUT
        networks = [self.reference_networks[AP_1]['2g']]
        self.add_networks(self.dut, networks)
        #make both AP_1 2G and AP_2 5G in range, and AP_1 5G
        #has much stronger RSSI than AP_2 2G
        self.attenuators[AP_1_5G_ATTENUATOR].set_atten(0)
        self.attenuators[AP_1_2G_ATTENUATOR].set_atten(50)
        #verify
        self.connect_and_verify_connected_bssid(
            self.reference_networks[AP_1]['5g']['bssid'])
        #bump up AP_1 2G RSSI and reduce AP_1 5G RSSI
        self.attenuators[AP_1_2G_ATTENUATOR].set_atten(0)
        self.attenuators[AP_1_5G_ATTENUATOR].set_atten(30)
        #ensure the time gap between two network selections
        time.sleep(NETWORK_SELECTION_TIME_GAP)
        #verify
        self.connect_and_verify_connected_bssid(
            self.reference_networks[AP_1]['2g']['bssid'])

    @test_tracker_info(uuid="ead78ae0-27ab-4bb8-ae77-0b9fe588436a")
    def test_network_selector_stay_on_sufficient_network(self):
        """
            1. Add two 5G WPA2 BSSIDs X and Y to the DUT. X has higher RSSI
               than Y.
            2. Connect the DUT to X.
            3. Change attenuation so that Y's RSSI goes above X's.
            4. Verify the DUT stays on X.
        """
        # add two saved networks to DUT
        networks = [
            self.reference_networks[AP_1]['5g'],
            self.reference_networks[AP_2]['5g']
        ]
        self.add_networks(self.dut, networks)

        # make both AP_1 5G and AP_2 5G in range, and AP_1 5G
        # has stronger RSSI than AP_2 5G
        self.attenuators[self.ap1_5g_attn].set_atten(LVL1_ATTN)
        self.attenuators[self.ap2_5g_attn].set_atten(LVL2_ATTN)
        time.sleep(ATTN_SLEEP)

        # verify DUT is connected to AP_1
        network = self.reference_networks[AP_1]['5g'].copy()
        if "OpenWrtAP" in self.user_params:
            network['bssid'] = self.bssid_map[AP_1]['5g'][network["SSID"]]
        self.connect_and_verify_connected_bssid(network)

        # bump up AP_2 5G RSSI over AP_1 5G RSSI
        self.attenuators[self.ap2_5g_attn].set_atten(MIN_ATTN)

        # ensure the time gap between two network selections
        time.sleep(NETWORK_SELECTION_TIME_GAP)

        # verify DUT is still connected to AP_1
        self.connect_and_verify_connected_bssid(network)

    @test_tracker_info(uuid="5470010f-8b62-4b1c-8b83-1f91422eced0")
    def test_network_selector_stay_on_user_selected_network(self):
        """
            1. Connect the DUT to SSID_A with a very low RSSI via the user select code path.
            2. Add SSID_B to the DUT as saved network. SSID_B has higher RSSI than SSID_A.
            3. Start a scan and network selection.
            4. Verify DUT stays on SSID_A.
        """
        # set max attenuation on AP_2 and make AP_1 5G in range with low RSSI
        self.attenuators[self.ap2_5g_attn].set_atten(MIN_ATTN)
        self.attenuators[self.ap1_5g_attn].set_atten(LVL1_ATTN)
        time.sleep(ATTN_SLEEP)

        # connect to AP_1 via user selection and add, save AP_2
        wutils.connect_to_wifi_network(self.dut,
                                       self.reference_networks[AP_1]['5g'])
        networks = [self.reference_networks[AP_2]['5g']]
        self.add_networks(self.dut, networks)

        # ensure the time gap between two network selections
        time.sleep(NETWORK_SELECTION_TIME_GAP)

        # verify we are still connected to AP_1 5G
        network = self.reference_networks[AP_1]['5g'].copy()
        if "OpenWrtAP" in self.user_params:
            network['bssid'] = self.bssid_map[AP_1]['5g'][network["SSID"]]
        self.connect_and_verify_connected_bssid(network)

    @test_tracker_info(uuid="f08d8f73-8c94-42af-bba9-4c49bbf16420")
    def test_network_selector_reselect_after_forget_network(self):
        """
            1. Add two 5G BSSIDs X and Y to the DUT. X has higher RSSI
               than Y.
            2. Connect the DUT to X.
            3. Forget X.
            5. Verify the DUT reselect and connect to Y.
        """
        # add two networks to DUT
        networks = [
            self.reference_networks[AP_1]['5g'],
            self.reference_networks[AP_2]['5g']
        ]
        self.add_networks(self.dut, networks)

        # make both AP_1 5G and AP_2 5G in range. AP_1 5G has stronger
        # RSSI than AP_2 5G
        self.attenuators[self.ap1_5g_attn].set_atten(MIN_ATTN)
        self.attenuators[self.ap2_5g_attn].set_atten(LVL1_ATTN)
        time.sleep(ATTN_SLEEP)

        # verify DUT connected to AP1
        network = self.reference_networks[AP_1]['5g'].copy()
        if "OpenWrtAP" in self.user_params:
            network['bssid'] = self.bssid_map[AP_1]['5g'][network["SSID"]]
        self.connect_and_verify_connected_bssid(network)

        # forget AP_1
        wutils.wifi_forget_network(self.dut,
                                   self.reference_networks[AP_1]['5g']['SSID'])

        # verify DUT connected to AP2
        network = self.reference_networks[AP_2]['5g'].copy()
        if "OpenWrtAP" in self.user_params:
            network['bssid'] = self.bssid_map[AP_2]['5g'][network["SSID"]]
        self.connect_and_verify_connected_bssid(network)
