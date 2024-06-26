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

import itertools
import json
import logging
import pprint
import queue
import time

import acts.base_test
import acts.signals as signals
import acts_contrib.test_utils.wifi.wifi_test_utils as wutils

import acts.utils

from acts import asserts
from acts.test_decorators import test_tracker_info
from acts.controllers.iperf_server import IPerfServer
from acts_contrib.test_utils.bt.bt_test_utils import enable_bluetooth
from acts_contrib.test_utils.bt.bt_test_utils import disable_bluetooth
from acts_contrib.test_utils.wifi.WifiBaseTest import WifiBaseTest
from acts_contrib.test_utils.wifi.wifi_constants import\
    COEX_BAND, COEX_CHANNEL, COEX_POWER_CAP_DBM, KEY_COEX_UNSAFE_CHANNELS, KEY_COEX_RESTRICTIONS

WifiEnums = wutils.WifiEnums
# Default timeout used for reboot, toggle WiFi and Airplane mode,
# for the system to settle down after the operation.
DEFAULT_TIMEOUT = 10
BAND_2GHZ = 0
BAND_5GHZ = 1


class WifiManagerTest(WifiBaseTest):
    """Tests for APIs in Android's WifiManager class.

    Test Bed Requirement:
    * Two Android device
    * Several Wi-Fi networks visible to the device, including an open Wi-Fi
      network.
    """

    def __init__(self, configs):
        super().__init__(configs)
        self.enable_packet_log = True

    def setup_class(self):
        super().setup_class()

        self.dut = self.android_devices[0]
        wutils.wifi_test_device_init(self.dut)
        wutils.wifi_toggle_state(self.dut, True)

        self.dut_client = None
        if len(self.android_devices) > 1:
            self.dut_client = self.android_devices[1]
            wutils.wifi_test_device_init(self.dut_client)
            wutils.wifi_toggle_state(self.dut_client, True)

        req_params = []
        opt_param = [
            "open_network", "reference_networks", "iperf_server_address",
            "wpa_networks", "wep_networks", "coex_unsafe_channels",
            "coex_restrictions", "wifi6_models"
        ]
        self.unpack_userparams(
            req_param_names=req_params, opt_param_names=opt_param)

        if "AccessPoint" in self.user_params:
            self.legacy_configure_ap_and_start(wpa_network=True, wep_network=True)
        elif "OpenWrtAP" in self.user_params:
            self.openwrt = self.access_points[0]
            self.configure_openwrt_ap_and_start(open_network=True,
                                                wpa_network=True,
                                                wep_network=self.openwrt.is_version_under_20())

        asserts.assert_true(
            len(self.reference_networks) > 0,
            "Need at least one reference network with psk.")
        self.wpapsk_2g = self.reference_networks[0]["2g"]
        self.wpapsk_5g = self.reference_networks[0]["5g"]
        self.open_network_2g = self.open_network[0]["2g"]
        self.open_network_5g = self.open_network[0]["5g"]

        # Use local host as iperf server.
        asserts.assert_true(
          wutils.get_host_public_ipv4_address(),
          "The host has no public ip address")
        self.iperf_server_address = wutils.get_host_public_ipv4_address()
        self.iperf_server_port = wutils.get_iperf_server_port()
        try:
          self.iperf_server = IPerfServer(self.iperf_server_port)
          self.iperf_server.start()
          logging.info(f"IPerf server started on {self.iperf_server_port}")
        except Exception as e:
          raise signals.TestFailure("Failed to start iperf3 server: %s" % e)

    def setup_test(self):
        super().setup_test()
        for ad in self.android_devices:
            ad.droid.wakeLockAcquireBright()
            ad.droid.wakeUpNow()
        wutils.wifi_toggle_state(self.dut, True)

    def teardown_test(self):
        super().teardown_test()
        for ad in self.android_devices:
            ad.droid.wakeLockRelease()
            ad.droid.goToSleepNow()
        self.turn_location_off_and_scan_toggle_off()
        if self.dut.droid.wifiIsApEnabled():
            wutils.stop_wifi_tethering(self.dut)
        for ad in self.android_devices:
            wutils.reset_wifi(ad)
        self.log.debug("Toggling Airplane mode OFF")
        asserts.assert_true(
            acts.utils.force_airplane_mode(self.dut, False),
            "Can not turn airplane mode off: %s" % self.dut.serial)

        if self.dut.model in self.user_params["google_pixel_watch_models"]:
            if wutils.get_wear_wifimediator_disable_status(self.dut):
                wutils.disable_wear_wifimediator(self.dut, False)

    def teardown_class(self):
        self.iperf_server.stop()
        if "AccessPoint" in self.user_params:
            del self.user_params["reference_networks"]
            del self.user_params["open_network"]


    """Helper Functions"""

    def connect_to_wifi_network(self, params):
        """Connection logic for open and psk wifi networks.

        Args:
            params: A tuple of network info and AndroidDevice object.
        """
        network, ad = params
        droid = ad.droid
        ed = ad.ed
        SSID = network[WifiEnums.SSID_KEY]
        wutils.start_wifi_connection_scan_and_ensure_network_found(
            ad, SSID);
        wutils.wifi_connect(ad, network, num_of_tries=3)

    def get_connection_data(self, dut, network):
        """Get network id and ssid info from connection data.

        Args:
            dut: The Android device object under test.
            network: dict representing the network to connect to.

        Returns:
            A convenience dict with the connected network's ID and SSID.

        """
        params = (network, dut)
        self.connect_to_wifi_network(params)
        connect_data = dut.droid.wifiGetConnectionInfo()
        ssid_id_dict = dict()
        ssid_id_dict[WifiEnums.NETID_KEY] = connect_data[WifiEnums.NETID_KEY]
        ssid_id_dict[WifiEnums.SSID_KEY] = connect_data[WifiEnums.SSID_KEY]
        return ssid_id_dict

    def connect_multiple_networks(self, dut):
        """Connect to one 2.4GHz and one 5Ghz network.

        Args:
            dut: The Android device object under test.

        Returns:
            A list with the connection details for the 2GHz and 5GHz networks.

        """
        network_list = list()
        connect_2g_data = self.get_connection_data(dut, self.wpapsk_2g)
        network_list.append(connect_2g_data)
        connect_5g_data = self.get_connection_data(dut, self.wpapsk_5g)
        network_list.append(connect_5g_data)
        return network_list

    def get_enabled_network(self, network1, network2):
        """Check network status and return currently unconnected network.

        Args:
            network1: dict representing a network.
            network2: dict representing a network.

        Return:
            Network dict of the unconnected network.

        """
        wifi_info = self.dut.droid.wifiGetConnectionInfo()
        enabled = network1
        if wifi_info[WifiEnums.SSID_KEY] == network1[WifiEnums.SSID_KEY]:
            enabled = network2
        return enabled

    def check_configstore_networks(self, networks):
        """Verify that all previously configured networks are presistent after
           reboot.

        Args:
            networks: List of network dicts.

        Return:
            None. Raises TestFailure.

        """
        network_info = self.dut.droid.wifiGetConfiguredNetworks()
        if len(network_info) != len(networks):
            msg = (
                "Length of configured networks before and after reboot don't"
                " match. \nBefore reboot = %s \n After reboot = %s" %
                (networks, network_info))
            raise signals.TestFailure(msg)
        # For each network, check if it exists in configured list after reboot
        current_ssids = set()
        for network in networks:
            exists = wutils.match_networks({
                WifiEnums.SSID_KEY: network[WifiEnums.SSID_KEY]
            }, network_info)
            if not len(exists):
                raise signals.TestFailure("%s network is not present in the"
                                          " configured list after reboot" %
                                          network[WifiEnums.SSID_KEY])
            # Get the new network id for each network after reboot.
            network[WifiEnums.NETID_KEY] = exists[0]['networkId']
            if exists[0]['status'] == 'CURRENT':
                current_ssids.add(network[WifiEnums.SSID_KEY])
                # At any given point, there can only be one currently active
                # network, defined with 'status':'CURRENT'
                if len(current_ssids) > 1:
                    raise signals.TestFailure("More than one network showing"
                                              "as 'CURRENT' after reboot")

    def connect_to_wifi_network_with_id(self, network_id, network_ssid):
        """Connect to the given network using network id and verify SSID.

        Args:
            network_id: int Network Id of the network.
            network_ssid: string SSID of the network.

        Returns: True if connect using network id was successful;
                 False otherwise.

        """
        wutils.start_wifi_connection_scan_and_ensure_network_found(
            self.dut, network_ssid);
        wutils.wifi_connect_by_id(self.dut, network_id)
        connect_data = self.dut.droid.wifiGetConnectionInfo()
        connect_ssid = connect_data[WifiEnums.SSID_KEY]
        self.log.debug("Expected SSID = %s Connected SSID = %s" %
                       (network_ssid, connect_ssid))
        if connect_ssid != network_ssid:
            return False
        wutils.verify_11ax_wifi_connection(
            self.dut, self.wifi6_models, "wifi6_ap" in self.user_params)
        return True

    def run_iperf_client(self, params):
        """Run iperf traffic after connection.

        Args:
            params: A tuple of network info and AndroidDevice object.
        """
        wait_time = 5
        network, ad = params
        SSID = network[WifiEnums.SSID_KEY]
        self.log.info("Starting iperf traffic through {}".format(SSID))
        time.sleep(wait_time)
        port_arg = "-p {}".format(self.iperf_server_port)
        success, data = ad.run_iperf_client(self.iperf_server_address,
                                            port_arg)
        self.log.debug(pprint.pformat(data))
        asserts.assert_true(success, "Error occurred in iPerf traffic.")

    def connect_to_wifi_network_toggle_wifi_and_run_iperf(self, params):
        """ Connect to the provided network and then toggle wifi mode and wait
        for reconnection to the provided network.

        Logic steps are
        1. Connect to the network.
        2. Turn wifi off.
        3. Turn wifi on.
        4. Wait for connection to the network.
        5. Run iperf traffic.

        Args:
            params: A tuple of network info and AndroidDevice object.
       """
        network, ad = params
        self.connect_to_wifi_network(params)
        wutils.toggle_wifi_and_wait_for_reconnection(
            ad, network, num_of_tries=5)
        self.run_iperf_client(params)

    def run_iperf(self, iperf_args):
        iperf_addr = self.iperf_server_address
        self.log.info("Running iperf client.")
        _, data = self.dut.run_iperf_client(iperf_addr, iperf_args)
        self.log.debug(data)

    def run_iperf_rx_tx(self, time, omit=10):
        args = "-p {} -t {} -O 10".format(self.iperf_server_port, time, omit)
        self.log.info("Running iperf client {}".format(args))
        self.run_iperf(args)
        args = "-p {} -t {} -O 10 -R".format(self.iperf_server_port, time,
                                             omit)
        self.log.info("Running iperf client {}".format(args))
        self.run_iperf(args)

    def get_energy_info(self):
        """ Steps:
            1. Check that the WiFi energy info reporting support on this device
               is as expected (support or not).
            2. If the device does not support energy info reporting as
               expected, skip the test.
            3. Call API to get WiFi energy info.
            4. Verify the values of "ControllerEnergyUsed" and
               "ControllerIdleTimeMillis" in energy info don't decrease.
            5. Repeat from Step 3 for 10 times.
        """
        # Check if dut supports energy info reporting.
        actual_support = self.dut.droid.wifiIsEnhancedPowerReportingSupported()
        model = self.dut.model
        if not actual_support:
            asserts.skip(
                ("Device %s does not support energy info reporting as "
                 "expected.") % model)
        # Verify reported values don't decrease.
        self.log.info(("Device %s supports energy info reporting, verify that "
                       "the reported values don't decrease.") % model)
        energy = 0
        idle_time = 0
        for i in range(10):
            info = self.dut.droid.wifiGetControllerActivityEnergyInfo()
            self.log.debug("Iteration %d, got energy info: %s" % (i, info))
            new_energy = info["ControllerEnergyUsed"]
            new_idle_time = info["ControllerIdleTimeMillis"]
            asserts.assert_true(new_energy >= energy,
                                "Energy value decreased: previous %d, now %d" %
                                (energy, new_energy))
            energy = new_energy
            asserts.assert_true(new_idle_time >= idle_time,
                                "Idle time decreased: previous %d, now %d" % (
                                    idle_time, new_idle_time))
            idle_time = new_idle_time
            wutils.start_wifi_connection_scan(self.dut)

    def turn_location_on_and_scan_toggle_on(self):
        """ Turns on wifi location scans.
        """
        acts.utils.set_location_service(self.dut, True)
        self.dut.droid.wifiScannerToggleAlwaysAvailable(True)
        msg = "Failed to turn on location service's scan."
        asserts.assert_true(self.dut.droid.wifiScannerIsAlwaysAvailable(), msg)

    def turn_location_off_and_scan_toggle_off(self):
        """ Turns off wifi location scans.
        """
        acts.utils.set_location_service(self.dut, False)
        self.dut.droid.wifiScannerToggleAlwaysAvailable(False)
        msg = "Failed to turn off location service's scan."
        asserts.assert_true(not self.dut.droid.wifiScannerIsAlwaysAvailable(), msg)

    def turn_location_on_and_scan_toggle_off(self):
        """ Turns off wifi location scans, but keeps location on.
        """
        acts.utils.set_location_service(self.dut, True)
        self.dut.droid.wifiScannerToggleAlwaysAvailable(False)
        msg = "Failed to turn off location service's scan."
        asserts.assert_true(not self.dut.droid.wifiScannerIsAlwaysAvailable(), msg)

    def helper_reconnect_toggle_wifi(self):
        """Connect to multiple networks, turn off/on wifi, then reconnect to
           a previously connected network.

        Steps:
        1. Connect to a 2GHz network.
        2. Connect to a 5GHz network.
        3. Turn WiFi OFF/ON.
        4. Reconnect to the non-current network.

        """
        connect_2g_data = self.get_connection_data(self.dut, self.wpapsk_2g)
        connect_5g_data = self.get_connection_data(self.dut, self.wpapsk_5g)
        wutils.toggle_wifi_off_and_on(self.dut)
        reconnect_to = self.get_enabled_network(connect_2g_data,
                                                connect_5g_data)
        reconnect = self.connect_to_wifi_network_with_id(
            reconnect_to[WifiEnums.NETID_KEY],
            reconnect_to[WifiEnums.SSID_KEY])
        if not reconnect:
            raise signals.TestFailure("Device did not connect to the correct"
                                      " network after toggling WiFi.")
        wutils.verify_11ax_wifi_connection(
            self.dut, self.wifi6_models, "wifi6_ap" in self.user_params)

    def helper_reconnect_toggle_airplane(self):
        """Connect to multiple networks, turn on/off Airplane moce, then
           reconnect a previously connected network.

        Steps:
        1. Connect to a 2GHz network.
        2. Connect to a 5GHz network.
        3. Turn ON/OFF Airplane mode.
        4. Reconnect to the non-current network.

        """
        connect_2g_data = self.get_connection_data(self.dut, self.wpapsk_2g)
        connect_5g_data = self.get_connection_data(self.dut, self.wpapsk_5g)
        wutils.toggle_airplane_mode_on_and_off(self.dut)
        reconnect_to = self.get_enabled_network(connect_2g_data,
                                                connect_5g_data)
        reconnect = self.connect_to_wifi_network_with_id(
            reconnect_to[WifiEnums.NETID_KEY],
            reconnect_to[WifiEnums.SSID_KEY])
        if not reconnect:
            raise signals.TestFailure("Device did not connect to the correct"
                                      " network after toggling Airplane mode.")
        wutils.verify_11ax_wifi_connection(
            self.dut, self.wifi6_models, "wifi6_ap" in self.user_params)

    def helper_reboot_configstore_reconnect(self, lock_screen=False):
        """Connect to multiple networks, reboot then reconnect to previously
           connected network.

        Steps:
        1. Connect to a 2GHz network.
        2. Connect to a 5GHz network.
        3. Reboot device.
        4. Verify all networks are persistent after reboot.
        5. Reconnect to the non-current network.

        """
        network_list = self.connect_multiple_networks(self.dut)
        network_list = self.dut.droid.wifiGetConfiguredNetworks()
        self.dut.reboot()
        time.sleep(DEFAULT_TIMEOUT)
        self.check_configstore_networks(network_list)

        reconnect_to = self.get_enabled_network(network_list[BAND_2GHZ],
                                                network_list[BAND_5GHZ])

        if lock_screen:
            self.dut.droid.wakeLockRelease()
            self.dut.droid.goToSleepNow()
        reconnect = self.connect_to_wifi_network_with_id(
            reconnect_to[WifiEnums.NETID_KEY],
            reconnect_to[WifiEnums.SSID_KEY])
        if not reconnect:
            raise signals.TestFailure(
                "Device failed to reconnect to the correct"
                " network after reboot.")
        wutils.verify_11ax_wifi_connection(
            self.dut, self.wifi6_models, "wifi6_ap" in self.user_params)

    def helper_toggle_wifi_reboot_configstore_reconnect(self):
        """Connect to multiple networks, disable WiFi, reboot, then
           reconnect to previously connected network.

        Steps:
        1. Connect to a 2GHz network.
        2. Connect to a 5GHz network.
        3. Turn WiFi OFF.
        4. Reboot device.
        5. Turn WiFi ON.
        4. Verify all networks are persistent after reboot.
        5. Reconnect to the non-current network.

        """
        network_list = self.connect_multiple_networks(self.dut)
        self.log.debug("Toggling wifi OFF")
        wutils.wifi_toggle_state(self.dut, False)
        time.sleep(DEFAULT_TIMEOUT)
        network_list = self.dut.droid.wifiGetConfiguredNetworks()
        self.dut.reboot()
        time.sleep(DEFAULT_TIMEOUT)
        self.log.debug("Toggling wifi ON")
        wutils.wifi_toggle_state(self.dut, True)
        time.sleep(DEFAULT_TIMEOUT)
        self.check_configstore_networks(network_list)
        reconnect_to = self.get_enabled_network(network_list[BAND_2GHZ],
                                                network_list[BAND_5GHZ])
        reconnect = self.connect_to_wifi_network_with_id(
            reconnect_to[WifiEnums.NETID_KEY],
            reconnect_to[WifiEnums.SSID_KEY])
        if not reconnect:
            msg = ("Device failed to reconnect to the correct network after"
                   " toggling WiFi and rebooting.")
            raise signals.TestFailure(msg)
        wutils.verify_11ax_wifi_connection(
            self.dut, self.wifi6_models, "wifi6_ap" in self.user_params)

    def helper_toggle_airplane_reboot_configstore_reconnect(self):
        """Connect to multiple networks, enable Airplane mode, reboot, then
           reconnect to previously connected network.

        Steps:
        1. Connect to a 2GHz network.
        2. Connect to a 5GHz network.
        3. Toggle Airplane mode ON.
        4. Reboot device.
        5. Toggle Airplane mode OFF.
        4. Verify all networks are persistent after reboot.
        5. Reconnect to the non-current network.

        """
        network_list = self.connect_multiple_networks(self.dut)
        self.log.debug("Toggling Airplane mode ON")
        asserts.assert_true(
            acts.utils.force_airplane_mode(self.dut, True),
            "Can not turn on airplane mode on: %s" % self.dut.serial)
        time.sleep(DEFAULT_TIMEOUT)
        network_list = self.dut.droid.wifiGetConfiguredNetworks()
        self.dut.reboot()
        time.sleep(DEFAULT_TIMEOUT)
        self.log.debug("Toggling Airplane mode OFF")
        asserts.assert_true(
            acts.utils.force_airplane_mode(self.dut, False),
            "Can not turn on airplane mode on: %s" % self.dut.serial)
        time.sleep(DEFAULT_TIMEOUT)
        self.check_configstore_networks(network_list)
        reconnect_to = self.get_enabled_network(network_list[BAND_2GHZ],
                                                network_list[BAND_5GHZ])
        reconnect = self.connect_to_wifi_network_with_id(
            reconnect_to[WifiEnums.NETID_KEY],
            reconnect_to[WifiEnums.SSID_KEY])
        if not reconnect:
            msg = ("Device failed to reconnect to the correct network after"
                   " toggling Airplane mode and rebooting.")
            raise signals.TestFailure(msg)
        wutils.verify_11ax_wifi_connection(
            self.dut, self.wifi6_models, "wifi6_ap" in self.user_params)

    def verify_traffic_between_devices(self,dest_device,src_device,num_of_tries=2):
        """Test the clients and DUT can ping each other.

        Args:
            num_of_tries: the retry times of ping test.
            dest_device:Test device.
            src_device:Second DUT access same AP
        """
        dest_device = dest_device.droid.connectivityGetIPv4Addresses('wlan0')[0]
        for _ in range(num_of_tries):
            if acts.utils.adb_shell_ping(src_device, count=10, dest_ip=dest_device, timeout=20):
                break
        else:
            asserts.fail("Ping to %s from %s failed" % (src_device.serial, dest_device))

    def ping_public_gateway_ip(self):
        """Ping 8.8.8.8"""
        try:
            ping_result = self.dut.adb.shell('ping -w 5 8.8.8.8')
            if '0%' in ping_result:
                self.dut.log.info('Ping success')
            return True
        except:
            self.dut.log.error('Faild to ping public gateway 8.8.8.8')
            return False

    """Tests"""

    @test_tracker_info(uuid="525fc5e3-afba-4bfd-9a02-5834119e3c66")
    def test_toggle_wifi_state_and_get_startupTime(self):
        """Test toggling wifi"""
        self.log.debug("Going from on to off.")
        wutils.wifi_toggle_state(self.dut, False)
        self.log.debug("Going from off to on.")
        startTime = time.time()
        wutils.wifi_toggle_state(self.dut, True)
        startup_time = time.time() - startTime
        self.log.debug("WiFi was enabled on the device in %s s." % startup_time)

    @test_tracker_info(uuid="e9d11563-2bbe-4c96-87eb-ec919b51435b")
    def test_toggle_with_screen(self):
        """Test toggling wifi with screen on/off"""
        wait_time = 5
        self.log.debug("Screen from off to on.")
        self.dut.droid.wakeLockAcquireBright()
        self.dut.droid.wakeUpNow()
        time.sleep(wait_time)
        self.log.debug("Going from on to off.")
        try:
            wutils.wifi_toggle_state(self.dut, False)
            time.sleep(wait_time)
            self.log.debug("Going from off to on.")
            wutils.wifi_toggle_state(self.dut, True)
        finally:
            self.dut.droid.wakeLockRelease()
            time.sleep(wait_time)
            self.dut.droid.goToSleepNow()

    @test_tracker_info(uuid="71556e06-7fb1-4e2b-9338-b01f1f8e286e")
    def test_scan(self):
        """Test wifi connection scan can start and find expected networks."""
        ssid = self.open_network_2g[WifiEnums.SSID_KEY]
        wutils.start_wifi_connection_scan_and_ensure_network_found(
            self.dut, ssid)
        ssid = self.open_network_5g[WifiEnums.SSID_KEY]
        wutils.start_wifi_connection_scan_and_ensure_network_found(
            self.dut, ssid)

    @test_tracker_info(uuid="3ea09efb-6921-429e-afb1-705ef5a09afa")
    def test_scan_with_wifi_off_and_location_scan_on(self):
        """Put wifi in scan only mode"""
        self.turn_location_on_and_scan_toggle_on()
        wutils.wifi_toggle_state(self.dut, False)

        """Test wifi connection scan can start and find expected networks."""
        ssid = self.open_network_2g[WifiEnums.SSID_KEY]
        wutils.start_wifi_connection_scan_and_ensure_network_found(
            self.dut, ssid)
        ssid = self.open_network_5g[WifiEnums.SSID_KEY]
        wutils.start_wifi_connection_scan_and_ensure_network_found(
            self.dut, ssid)

    @test_tracker_info(uuid="558652de-c802-405f-b9dc-b7fcc9237673")
    def test_scan_after_reboot_with_wifi_off_and_location_scan_on(self):
        """Put wifi in scan only mode"""
        self.turn_location_on_and_scan_toggle_on()
        wutils.wifi_toggle_state(self.dut, False)

        # Reboot the device.
        self.dut.reboot()
        time.sleep(DEFAULT_TIMEOUT)

        """Test wifi connection scan can start and find expected networks."""
        ssid = self.open_network_2g[WifiEnums.SSID_KEY]
        wutils.start_wifi_connection_scan_and_ensure_network_found(
            self.dut, ssid)
        ssid = self.open_network_5g[WifiEnums.SSID_KEY]
        wutils.start_wifi_connection_scan_and_ensure_network_found(
            self.dut, ssid)

    @test_tracker_info(uuid="770caebe-bcb1-43ac-95b6-5dd52dd90e80")
    def test_scan_with_wifi_off_and_location_scan_off(self):
        """Turn off wifi and location scan"""
        self.turn_location_on_and_scan_toggle_off()

        if self.dut.model in self.user_params["google_pixel_watch_models"]:
            wutils.disable_wear_wifimediator(self.dut, True)

        wutils.wifi_toggle_state(self.dut, False)

        """Test wifi connection scan should fail."""
        self.dut.droid.wifiStartScan()
        try:
            self.dut.ed.pop_event("WifiManagerScanResultsAvailable", 60)
        except queue.Empty:
            self.log.debug("Wifi scan results not received.")
        else:
            asserts.fail("Wi-Fi scan results received")

    @test_tracker_info(uuid="a4ad9930-a8fa-4868-81ed-a79c7483e502")
    def test_add_network(self):
        """Test wifi connection scan."""
        ssid = self.open_network_2g[WifiEnums.SSID_KEY]
        nId = self.dut.droid.wifiAddNetwork(self.open_network_2g)
        asserts.assert_true(nId > -1, "Failed to add network.")
        configured_networks = self.dut.droid.wifiGetConfiguredNetworks()
        self.log.debug(
            ("Configured networks after adding: %s" % configured_networks))
        wutils.assert_network_in_list({
            WifiEnums.SSID_KEY: ssid
        }, configured_networks)

    @test_tracker_info(uuid="aca85551-10ba-4007-90d9-08bcdeb16a60")
    def test_forget_network(self):
        ssid = self.open_network_2g[WifiEnums.SSID_KEY]
        nId = self.dut.droid.wifiAddNetwork(self.open_network_2g)
        asserts.assert_true(nId > -1, "Failed to add network.")
        configured_networks = self.dut.droid.wifiGetConfiguredNetworks()
        self.log.debug(
            ("Configured networks after adding: %s" % configured_networks))
        wutils.assert_network_in_list({
            WifiEnums.SSID_KEY: ssid
        }, configured_networks)
        wutils.wifi_forget_network(self.dut, ssid)
        configured_networks = self.dut.droid.wifiGetConfiguredNetworks()
        for nw in configured_networks:
            asserts.assert_true(
                nw[WifiEnums.BSSID_KEY] != ssid,
                "Found forgotten network %s in configured networks." % ssid)

    @test_tracker_info(uuid="3cff17f6-b684-4a95-a438-8272c2ad441d")
    def test_reconnect_to_previously_connected(self):
        """Connect to multiple networks and reconnect to the previous network.

        Steps:
        1. Connect to a 2GHz network.
        2. Connect to a 5GHz network.
        3. Reconnect to the 2GHz network using its network id.
        4. Reconnect to the 5GHz network using its network id.

        """
        connect_2g_data = self.get_connection_data(self.dut, self.wpapsk_2g)
        connect_5g_data = self.get_connection_data(self.dut, self.wpapsk_5g)
        reconnect_2g = self.connect_to_wifi_network_with_id(
            connect_2g_data[WifiEnums.NETID_KEY],
            connect_2g_data[WifiEnums.SSID_KEY])
        if not reconnect_2g:
            raise signals.TestFailure("Device did not connect to the correct"
                                      " 2GHz network.")
        reconnect_5g = self.connect_to_wifi_network_with_id(
            connect_5g_data[WifiEnums.NETID_KEY],
            connect_5g_data[WifiEnums.SSID_KEY])
        if not reconnect_5g:
            raise signals.TestFailure("Device did not connect to the correct"
                                      " 5GHz network.")

    @test_tracker_info(uuid="334175c3-d26a-4c87-a8ab-8eb220b2d80f")
    def test_reconnect_toggle_wifi(self):
        """Connect to multiple networks, turn off/on wifi, then reconnect to
           a previously connected network.

        Steps:
        1. Connect to a 2GHz network.
        2. Connect to a 5GHz network.
        3. Turn WiFi OFF/ON.
        4. Reconnect to the non-current network.

        """
        self.helper_reconnect_toggle_wifi()

    @test_tracker_info(uuid="bd2cec9e-7f17-44ef-8a0c-4da92a9b55ae")
    def test_reconnect_toggle_wifi_with_location_scan_on(self):
        """Connect to multiple networks, turn off/on wifi, then reconnect to
           a previously connected network.

        Steps:
        1. Turn on location scans.
        2. Connect to a 2GHz network.
        3. Connect to a 5GHz network.
        4. Turn WiFi OFF/ON.
        5. Reconnect to the non-current network.

        """
        self.turn_location_on_and_scan_toggle_on()
        self.helper_reconnect_toggle_wifi()

    @test_tracker_info(uuid="8e6e6c21-fefb-4fe8-9fb1-f09b1182b76d")
    def test_reconnect_toggle_airplane(self):
        """Connect to multiple networks, turn on/off Airplane moce, then
           reconnect a previously connected network.

        Steps:
        1. Connect to a 2GHz network.
        2. Connect to a 5GHz network.
        3. Turn ON/OFF Airplane mode.
        4. Reconnect to the non-current network.

        """
        self.helper_reconnect_toggle_airplane()

    @test_tracker_info(uuid="28562f13-8a0a-492e-932c-e587560db5f2")
    def test_reconnect_toggle_airplane_with_location_scan_on(self):
        """Connect to multiple networks, turn on/off Airplane moce, then
           reconnect a previously connected network.

        Steps:
        1. Turn on location scans.
        2. Connect to a 2GHz network.
        3. Connect to a 5GHz network.
        4. Turn ON/OFF Airplane mode.
        5. Reconnect to the non-current network.

        """
        self.turn_location_on_and_scan_toggle_on()
        self.helper_reconnect_toggle_airplane()

    @test_tracker_info(uuid="52b89a47-f260-4343-922d-fbeb4d8d2b63")
    def test_reconnect_toggle_wifi_on_with_airplane_on(self):
        """Connect to multiple networks, turn on airplane mode, turn on wifi,
        then reconnect a previously connected network.

        Steps:
        1. Connect to a 2GHz network.
        2. Connect to a 5GHz network.
        3. Turn ON Airplane mode.
        4. Turn ON WiFi.
        5. Reconnect to the a previously connected network.
        """
        connect_2g_data = self.get_connection_data(self.dut, self.wpapsk_2g)
        connect_5g_data = self.get_connection_data(self.dut, self.wpapsk_5g)
        self.log.debug("Toggling Airplane mode ON")
        asserts.assert_true(
            acts.utils.force_airplane_mode(self.dut, True),
            "Can not turn on airplane mode on: %s" % self.dut.serial)
        self.log.debug("Toggling wifi ON")
        wutils.wifi_toggle_state(self.dut, True)
        time.sleep(DEFAULT_TIMEOUT)
        reconnect_to = self.get_enabled_network(connect_2g_data,
                                                connect_5g_data)
        reconnect = self.connect_to_wifi_network_with_id(
            reconnect_to[WifiEnums.NETID_KEY],
            reconnect_to[WifiEnums.SSID_KEY])
        if not reconnect:
            raise signals.TestFailure("Device did not connect to the correct"
                                      " network after toggling WiFi.")

    @test_tracker_info(uuid="2dddc734-e9f6-4d30-9c2d-4368e721a350")
    def test_verify_airplane_mode_on_with_wifi_disabled(self):
        """Connect to multiple networks, turn on airplane mode, turn off Wi-Fi,
        then make sure there is no internet.

        Steps:
        1. Connect to a 2GHz network.
        2. Connect to a 5GHz network.
        3. Turn ON Airplane mode.
        4. Turn OFF WiFi.
        5. Ping to make sure there is no internet
        """
        connect_2g_data = self.get_connection_data(self.dut, self.wpapsk_2g)
        connect_5g_data = self.get_connection_data(self.dut, self.wpapsk_5g)
        self.log.debug("Toggling Airplane mode ON")
        asserts.assert_true(
            acts.utils.force_airplane_mode(self.dut, True),
            "Can not turn on airplane mode on: %s" % self.dut.serial)
        self.log.debug("Toggling Wi-Fi OFF")
        wutils.wifi_toggle_state(self.dut, False)
        time.sleep(DEFAULT_TIMEOUT)
        if self.ping_public_gateway_ip():
            raise signals.TestFailure("Device has internet after"
                                             " toggling WiFi off.")

    @test_tracker_info(uuid="3d041c12-05e2-46a7-ab9b-e3f60cc735db")
    def test_reboot_configstore_reconnect(self):
        """Connect to multiple networks, reboot then reconnect to previously
           connected network.

        Steps:
        1. Connect to a 2GHz network.
        2. Connect to a 5GHz network.
        3. Reboot device.
        4. Verify all networks are persistent after reboot.
        5. Reconnect to the non-current network.

        """
        self.helper_reboot_configstore_reconnect()

    @test_tracker_info(uuid="a70d5853-67b5-4d48-bdf7-08ee51fafd21")
    def test_reboot_configstore_reconnect_with_location_scan_on(self):
        """Connect to multiple networks, reboot then reconnect to previously
           connected network.

        Steps:
        1. Turn on location scans.
        2. Connect to a 2GHz network.
        3. Connect to a 5GHz network.
        4. Reboot device.
        5. Verify all networks are persistent after reboot.
        6. Reconnect to the non-current network.

        """
        self.turn_location_on_and_scan_toggle_on()
        self.helper_reboot_configstore_reconnect()

    @test_tracker_info(uuid="26d94dfa-1349-4c8b-aea0-475eb73bb521")
    def test_toggle_wifi_reboot_configstore_reconnect(self):
        """Connect to multiple networks, disable WiFi, reboot, then
           reconnect to previously connected network.

        Steps:
        1. Connect to a 2GHz network.
        2. Connect to a 5GHz network.
        3. Turn WiFi OFF.
        4. Reboot device.
        5. Turn WiFi ON.
        4. Verify all networks are persistent after reboot.
        5. Reconnect to the non-current network.

        """
        self.helper_toggle_wifi_reboot_configstore_reconnect()

    @test_tracker_info(uuid="7c004a3b-c1c6-4371-9124-0f34650be915")
    def test_toggle_wifi_reboot_configstore_reconnect_with_location_scan_on(self):
        """Connect to multiple networks, disable WiFi, reboot, then
           reconnect to previously connected network.

        Steps:
        1. Turn on location scans.
        2. Connect to a 2GHz network.
        3. Connect to a 5GHz network.
        4. Turn WiFi OFF.
        5. Reboot device.
        6. Turn WiFi ON.
        7. Verify all networks are persistent after reboot.
        8. Reconnect to the non-current network.

        """
        self.turn_location_on_and_scan_toggle_on()
        self.helper_toggle_wifi_reboot_configstore_reconnect()

    @test_tracker_info(uuid="4fce017b-b443-40dc-a598-51d59d3bb38f")
    def test_toggle_airplane_reboot_configstore_reconnect(self):
        """Connect to multiple networks, enable Airplane mode, reboot, then
           reconnect to previously connected network.

        Steps:
        1. Connect to a 2GHz network.
        2. Connect to a 5GHz network.
        3. Toggle Airplane mode ON.
        4. Reboot device.
        5. Toggle Airplane mode OFF.
        4. Verify all networks are persistent after reboot.
        5. Reconnect to the non-current network.

        """
        self.helper_toggle_airplane_reboot_configstore_reconnect()

    @test_tracker_info(uuid="7f0810f9-2338-4158-95f5-057f5a1905b6")
    def test_toggle_airplane_reboot_configstore_reconnect_with_location_scan_on(self):
        """Connect to multiple networks, enable Airplane mode, reboot, then
           reconnect to previously connected network.

        Steps:
        1. Turn on location scans.
        2. Connect to a 2GHz network.
        3. Connect to a 5GHz network.
        4. Toggle Airplane mode ON.
        5. Reboot device.
        6. Toggle Airplane mode OFF.
        7. Verify all networks are persistent after reboot.
        8. Reconnect to the non-current network.

        """
        self.turn_location_on_and_scan_toggle_on()
        self.helper_toggle_airplane_reboot_configstore_reconnect()

    @test_tracker_info(uuid="342c13cb-6508-4942-bee3-07c5d20d92a5")
    def test_reboot_configstore_reconnect_with_screen_lock(self):
        """Verify device can re-connect to configured networks after reboot.

        Steps:
        1. Connect to 2G and 5G networks.
        2. Reboot device
        3. Verify device connects to 1 network automatically.
        4. Lock screen and verify device can connect to the other network.
        """
        self.helper_reboot_configstore_reconnect(lock_screen=True)

    @test_tracker_info(uuid="7e6050d9-79b1-4726-80cf-686bb99b8945")
    def test_connect_to_5g_after_reboot_without_unlock(self):
        """Connect to 5g network afer reboot without unlock.

        Steps:
        1. Reboot device and lock screen
        2. Connect to 5G network and verify it works.
        """
        self.dut.reboot()
        time.sleep(DEFAULT_TIMEOUT)
        self.dut.droid.wakeLockRelease()
        self.dut.droid.goToSleepNow()
        wutils.connect_to_wifi_network(self.dut, self.wpapsk_5g)
        wutils.verify_11ax_wifi_connection(
            self.dut, self.wifi6_models, "wifi6_ap" in self.user_params)

    @test_tracker_info(uuid="81eb7527-4c92-4422-897a-6b5f6445e84a")
    def test_config_store_with_wpapsk_2g(self):
        self.connect_to_wifi_network_toggle_wifi_and_run_iperf(
            (self.wpapsk_2g, self.dut))
        wutils.verify_11ax_wifi_connection(
            self.dut, self.wifi6_models, "wifi6_ap" in self.user_params)

    @test_tracker_info(uuid="8457903d-cb7e-4c89-bcea-7f59585ea6e0")
    def test_config_store_with_wpapsk_5g(self):
        self.connect_to_wifi_network_toggle_wifi_and_run_iperf(
            (self.wpapsk_5g, self.dut))
        wutils.verify_11ax_wifi_connection(
            self.dut, self.wifi6_models, "wifi6_ap" in self.user_params)

    @test_tracker_info(uuid="b9fbc13a-47b4-4f64-bd2c-e5a3cb24ab2f")
    def test_tdls_supported(self):
        model = self.dut.model
        self.log.debug("Model is %s" % model)
        if not model.startswith("volantis"):
            asserts.assert_true(self.dut.droid.wifiIsTdlsSupported(), (
                "TDLS should be supported on %s, but device is "
                "reporting not supported.") % model)
        else:
            asserts.assert_false(self.dut.droid.wifiIsTdlsSupported(), (
                "TDLS should not be supported on %s, but device "
                "is reporting supported.") % model)

    @test_tracker_info(uuid="50637d40-ea59-4f4b-9fc1-e6641d64074c")
    def test_energy_info(self):
        """Verify the WiFi energy info reporting feature """
        self.get_energy_info()

    @test_tracker_info(uuid="1f1cf549-53eb-4f36-9f33-ce06c9158efc")
    def test_energy_info_connected(self):
        """Verify the WiFi energy info reporting feature when connected.

        Connect to a wifi network, then the same as test_energy_info.
        """
        wutils.wifi_connect(self.dut, self.open_network_2g)
        self.get_energy_info()
        wutils.verify_11ax_wifi_connection(
            self.dut, self.wifi6_models, "wifi6_ap" in self.user_params)

    @test_tracker_info(uuid="2622c253-defc-4a35-93a6-ca9d29a8238c")
    def test_connect_to_wep_2g(self):
        """Verify DUT can connect to 2GHz WEP network

        Steps:
        1. Ensure the 2GHz WEP network is visible in scan result.
        2. Connect to the network and validate internet connection.
        """
        asserts.skip_if(
            hasattr(self, "openwrt") and not self.access_points[0].is_version_under_20(),
            "OpenWrt no longer support wep network."
        )
        wutils.connect_to_wifi_network(self.dut, self.wep_networks[0]["2g"])

    @test_tracker_info(uuid="1f2d17a2-e92d-43af-966b-3421c0db8620")
    def test_connect_to_wep_5g(self):
        """Verify DUT can connect to 5GHz WEP network

        Steps:
        1. Ensure the 5GHz WEP network is visible in scan result.
        2. Connect to the network and validate internet connection.
        """
        asserts.skip_if(
            hasattr(self, "openwrt") and not self.access_points[0].is_version_under_20(),
            "OpenWrt no longer support wep network."
        )
        wutils.connect_to_wifi_network(self.dut, self.wep_networks[0]["5g"])

    @test_tracker_info(uuid="4a957952-289d-4657-9882-e1475274a7ff")
    def test_connect_to_wpa_2g(self):
        """Verify DUT can connect to 2GHz WPA-PSK network

        Steps:
        1. Ensure the 2GHz WPA-PSK network is visible in scan result.
        2. Connect to the network and validate internet connection.
        """
        wutils.connect_to_wifi_network(self.dut, self.wpa_networks[0]["2g"])
        wutils.verify_11ax_wifi_connection(
            self.dut, self.wifi6_models, "wifi6_ap" in self.user_params)

    @test_tracker_info(uuid="612c3c31-a4c5-4014-9a2d-3f4bcc20c0d7")
    def test_connect_to_wpa_5g(self):
        """Verify DUT can connect to 5GHz WPA-PSK network

        Steps:
        1. Ensure the 5GHz WPA-PSK network is visible in scan result.
        2. Connect to the network and validate internet connection.
        """
        wutils.connect_to_wifi_network(self.dut, self.wpa_networks[0]["5g"])
        wutils.verify_11ax_wifi_connection(
            self.dut, self.wifi6_models, "wifi6_ap" in self.user_params)

    @test_tracker_info(uuid="2a617fb4-1d8e-44e9-a500-a5456e1df83f")
    def test_connect_to_2g_can_be_pinged(self):
        """Verify DUT can be pinged by another device when it connects to 2GHz AP

        Steps:
        1. Ensure the 2GHz WPA-PSK network is visible in scan result.
        2. Connect to the network and validate internet connection.
        3. Check DUT can be pinged by another device
        """
        wutils.connect_to_wifi_network(self.dut, self.wpa_networks[0]["2g"])
        wutils.verify_11ax_wifi_connection(
            self.dut, self.wifi6_models, "wifi6_ap" in self.user_params)
        wutils.connect_to_wifi_network(self.dut_client, self.wpa_networks[0]["2g"])
        wutils.verify_11ax_wifi_connection(
            self.dut_client, self.wifi6_models, "wifi6_ap" in self.user_params)
        self.verify_traffic_between_devices(self.dut,self.dut_client)

    @test_tracker_info(uuid="94bdd657-649b-4a2c-89c3-3ec6ba18e08e")
    def test_connect_to_5g_can_be_pinged(self):
        """Verify DUT can be pinged by another device when it connects to 5GHz AP

        Steps:
        1. Ensure the 5GHz WPA-PSK network is visible in scan result.
        2. Connect to the network and validate internet connection.
        3. Check DUT can be pinged by another device
        """
        wutils.connect_to_wifi_network(self.dut, self.wpa_networks[0]["5g"])
        wutils.verify_11ax_wifi_connection(
            self.dut, self.wifi6_models, "wifi6_ap" in self.user_params)
        wutils.connect_to_wifi_network(self.dut_client, self.wpa_networks[0]["5g"])
        wutils.verify_11ax_wifi_connection(
            self.dut_client, self.wifi6_models, "wifi6_ap" in self.user_params)
        self.verify_traffic_between_devices(self.dut,self.dut_client)

    @test_tracker_info(uuid="d87359aa-c4da-4554-b5de-8e3fa852a6b0")
    def test_sta_turn_off_screen_can_be_pinged(self):
        """Verify DUT can be pinged by another device after idle for a while

        Steps:
        1. Ensure the 2GHz WPA-PSK network is visible in scan result.
        2. DUT and DUT_Client connect to the network and validate internet connection.
        3. Let DUT sleep for 5 minutes
        4. Check DUT can be pinged by DUT_Client
        """
        asserts.skip_if(len(self.android_devices) < 3, "Need 3 devices")
        self.dut_client_a = self.android_devices[1]
        self.dut_client_b = self.android_devices[2]

        # enable hotspot on dut and connect client devices to it
        ap_ssid = "softap_" + acts.utils.rand_ascii_str(8)
        ap_password = acts.utils.rand_ascii_str(8)
        self.dut.log.info("softap setup: %s %s", ap_ssid, ap_password)
        config = {wutils.WifiEnums.SSID_KEY: ap_ssid}
        config[wutils.WifiEnums.PWD_KEY] = ap_password
        wutils.start_wifi_tethering(
            self.dut,
            config[wutils.WifiEnums.SSID_KEY],
            config[wutils.WifiEnums.PWD_KEY],
            wutils.WifiEnums.WIFI_CONFIG_APBAND_AUTO)

        # DUT connect to AP
        wutils.connect_to_wifi_network(
            self.dut_client_a, config, check_connectivity=False)
        wutils.connect_to_wifi_network(
            self.dut_client_b, config, check_connectivity=False)
        # Check DUT and DUT_Client can ping each other successfully
        self.verify_traffic_between_devices(self.dut_client_a,
                                            self.dut_client_b)
        self.verify_traffic_between_devices(self.dut_client_a,
                                            self.dut_client_b)

        # DUT turn off screen and go sleep for 5 mins
        self.dut.droid.wakeLockRelease()
        self.dut.droid.goToSleepNow()
        # TODO(hsiuchangchen): find a way to check system already suspended
        #                      instead of waiting 5 mins
        self.log.info("Sleep for 5 minutes")
        time.sleep(300)
        # Verify DUT_Client can ping DUT when DUT sleeps
        self.verify_traffic_between_devices(self.dut_client_a,
                                            self.dut_client_b)
        self.dut.droid.wakeLockAcquireBright()
        self.dut.droid.wakeUpNow()

    @test_tracker_info(uuid="25e8dd62-ae9f-46f7-96aa-030fee95dfda")
    def test_wifi_saved_network_reset(self):
        """Verify DUT can reset Wi-Fi saved network list after add a network.

        Steps:
        1. Connect to a 2GHz network
        2. Reset the Wi-Fi saved network
        3. Verify the saved network has been clear
        """
        ssid = self.open_network_2g[WifiEnums.SSID_KEY]
        nId = self.dut.droid.wifiAddNetwork(self.open_network_2g)
        asserts.assert_true(nId > -1, "Failed to add network.")
        configured_networks = self.dut.droid.wifiGetConfiguredNetworks()
        self.log.debug(
            ("Configured networks after adding: %s" % configured_networks))
        wutils.assert_network_in_list({
            WifiEnums.SSID_KEY: ssid
        }, configured_networks)
        self.dut.droid.wifiFactoryReset()
        configured_networks = self.dut.droid.wifiGetConfiguredNetworks()
        for nw in configured_networks:
            asserts.assert_true(
                nw[WifiEnums.BSSID_KEY] != ssid,
                "Found saved network %s in configured networks." % ssid)

    @test_tracker_info(uuid="402cfaa8-297f-4865-9e27-6bab6adca756")
    def test_reboot_wifi_and_bluetooth_on(self):
        """Toggle WiFi and bluetooth ON then reboot """
        wutils.wifi_toggle_state(self.dut, True)
        enable_bluetooth(self.dut.droid, self.dut.ed)

        self.dut.reboot()
        time.sleep(DEFAULT_TIMEOUT)

        asserts.assert_true(self.dut.droid.bluetoothCheckState(),
                "bluetooth state changed after reboot")
        asserts.assert_true(self.dut.droid.wifiCheckState(),
                "wifi state changed after reboot")

        disable_bluetooth(self.dut.droid)

    @test_tracker_info(uuid="d0e14a2d-a28f-4551-8988-1e15d9d8bb1a")
    def test_scan_result_api(self):
        """Register scan result callback, start scan and wait for event"""
        self.dut.ed.clear_all_events()
        self.dut.droid.wifiStartScanWithListener()
        try:
            events = self.dut.ed.pop_events(
                "WifiManagerScanResultsCallbackOnSuccess", 60)
        except queue.Empty:
            asserts.fail(
                "Wi-Fi scan results did not become available within 60s.")

    @test_tracker_info(uuid="03cfbc86-7fcc-48d8-ab0f-1f6f3523e596")
    def test_enable_disable_auto_join_saved_network(self):
        """
        Add a saved network, simulate user change the auto join to false, ensure the device doesn't
        auto connect to this network

        Steps:
        1. Create a saved network.
        2. Add this saved network, and ensure we connect to this network
        3. Simulate user change the auto join to false.
        4. Toggle the Wifi off and on
        4. Ensure device doesn't connect to his network
        """
        network = self.open_network_5g
        wutils.connect_to_wifi_network(self.dut, network)
        wutils.verify_11ax_wifi_connection(
            self.dut, self.wifi6_models, "wifi6_ap" in self.user_params)
        info = self.dut.droid.wifiGetConnectionInfo()
        network_id = info[WifiEnums.NETID_KEY]
        self.dut.log.info("Disable auto join on network")
        self.dut.droid.wifiEnableAutojoin(network_id, False)
        wutils.wifi_toggle_state(self.dut, False)
        wutils.wifi_toggle_state(self.dut, True)
        asserts.assert_false(
            wutils.wait_for_connect(self.dut, network[WifiEnums.SSID_KEY],
                                    assert_on_fail=False), "Device should not connect.")
        self.dut.droid.wifiEnableAutojoin(network_id, True)
        wutils.wait_for_connect(self.dut, network[WifiEnums.SSID_KEY], assert_on_fail=False)
        wutils.verify_11ax_wifi_connection(
            self.dut, self.wifi6_models, "wifi6_ap" in self.user_params)

    def coex_unsafe_channel_key(self, unsafe_channel):
        if COEX_POWER_CAP_DBM in unsafe_channel:
            return (unsafe_channel[COEX_BAND], unsafe_channel[COEX_CHANNEL],
                    unsafe_channel[COEX_POWER_CAP_DBM])
        return (unsafe_channel[COEX_BAND], unsafe_channel[COEX_CHANNEL])

    @test_tracker_info(uuid="78558b30-3792-4a1f-bb56-34bbbbce6ac8")
    def test_set_get_coex_unsafe_channels(self):
        """
        Set the unsafe channels to avoid for coex, then retrieve the active values and compare to
        values set. If the default algorithm is enabled, then ensure that the active values are
        unchanged.

        Steps:
        1. Register a coex callback and listen for the update event to get the current coex values.
        2. Create list of coex unsafe channels and restrictions

            coex_unsafe_channels format:
                [
                    {
                        "band": <"24_GHZ" or "5_GHZ">
                        "channel" : <Channel number>
                        (Optional) "powerCapDbm" : <Power Cap in Dbm>
                    }
                    ...
                ]

            coex_restrictions format:
                [
                    (Optional) "WIFI_DIRECT",
                    (Optional) "SOFTAP",
                    (Optional) "WIFI_AWARE"
                ]
        3. Set these values as the active values and listen for the update event.
        4. If the default algorithm is enabled, expect to not get the update event. If it is
           disabled, compare the updated values and see if they are the same as the provided values.
        5. Restore the previous values if the test values were set.
        """
        asserts.skip_if(not self.dut.droid.isSdkAtLeastS(),
                        "Require SDK at least S to use wifi coex apis.")
        self.dut.ed.clear_all_events()

        # Register a coex callback to start receiving coex events
        self.dut.droid.wifiRegisterCoexCallback()
        try:
            # Wait for the immediate callback from registering and store the current values
            event = self.dut.ed.pop_event("WifiManagerCoexCallback#onCoexUnsafeChannelsChanged", 5)
        except queue.Empty:
            asserts.fail("Coex callback event not received after registering.")
        prev_unsafe_channels = sorted(json.loads(event["data"][KEY_COEX_UNSAFE_CHANNELS]),
                                      key=self.coex_unsafe_channel_key)
        prev_restrictions = sorted(json.loads(event["data"][KEY_COEX_RESTRICTIONS]))

        # Set new values for coex unsafe channels
        test_unsafe_channels = sorted(self.coex_unsafe_channels,
                                      key=self.coex_unsafe_channel_key)
        test_restrictions = sorted(self.coex_restrictions)
        self.dut.droid.wifiSetCoexUnsafeChannels(test_unsafe_channels, test_restrictions)
        try:
            # Wait for the callback from setting the coex unsafe channels
            event = self.dut.ed.pop_event("WifiManagerCoexCallback#onCoexUnsafeChannelsChanged", 5)
            # Callback received. This should be expected only if default algo is disabled.
            asserts.assert_false(self.dut.droid.wifiIsDefaultCoexAlgorithmEnabled(),
                                "Default algo was enabled but Coex callback received after"
                                " setCoexUnsafeChannels")
            curr_unsafe_channels = sorted(json.loads(event["data"][KEY_COEX_UNSAFE_CHANNELS]),
                                          key=self.coex_unsafe_channel_key)
            curr_restrictions = sorted(json.loads(event["data"][KEY_COEX_RESTRICTIONS]))
            # Compare the current values with the set values
            asserts.assert_true(curr_unsafe_channels == test_unsafe_channels,
                                "default coex algorithm disabled but current unsafe channels "
                                + str(curr_unsafe_channels)
                                + " do not match the set values " + str(test_unsafe_channels))
            asserts.assert_true(curr_restrictions == test_restrictions,
                                "default coex algorithm disabled but current restrictions "
                                + str(curr_restrictions)
                                + " do not match the set values " + str(test_restrictions))
            # Restore the previous values
            self.dut.droid.wifiSetCoexUnsafeChannels(prev_unsafe_channels, prev_restrictions)
        except queue.Empty:
            # Callback not received. This should be expected only if the default algo is enabled.
            asserts.assert_true(self.dut.droid.wifiIsDefaultCoexAlgorithmEnabled(),
                                "Default algo was disabled but Coex callback not received after"
                                " setCoexUnsafeChannels")

        self.dut.droid.wifiUnregisterCoexCallback()
