#!/usr/bin/env python3.4
#
#   Copyright 2018 - The Android Open Source Project
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
import time

import acts.base_test
import acts.signals as signals
import acts_contrib.test_utils.wifi.wifi_test_utils as wutils
import acts.utils

from acts import asserts
from acts.test_decorators import test_tracker_info
from acts_contrib.test_utils.wifi.WifiBaseTest import WifiBaseTest

WifiEnums = wutils.WifiEnums
# Timeout used for crash recovery.
RECOVERY_TIMEOUT = 15
WIFICOND_KILL_SHELL_COMMAND = "killall wificond"
SUPPLICANT_KILL_SHELL_COMMAND = "killall wpa_supplicant"
WIFI_VENDOR_EXT_HAL_DAEMON = "vendor.google.wifi_ext@1.0-service-vendor"
WIFI_VENDOR_EXT_HAL_DAEMON_PREFIX = "vendor.google.wifi_ext@"
WIFI_VENDOR_EXT_HAL_DAEMON_KILL_SHELL_COMMAND = "killall vendor.google.wifi_ext@1.0-service-vendor"
WIFI_VENDOR_HAL_DAEMON = "vendor.google.wifi_ext-service-vendor"
WIFI_VENDOR_HAL_DAEMON_KILL_SHELL_COMMAND = "killall vendor.google.wifi_ext-service-vendor"


class WifiCrashTest(WifiBaseTest):
    """Crash Tests for wifi stack.

    Test Bed Requirement:
    * One Android device
    * One Wi-Fi network visible to the device.
    """

    def __init__(self, configs):
        super().__init__(configs)
        self.enable_packet_log = True

    def setup_class(self):
        super().setup_class()

        self.dut = self.android_devices[0]
        wutils.wifi_test_device_init(self.dut)
        req_params = []
        opt_param = ["reference_networks"]
        self.unpack_userparams(req_param_names=req_params,
                               opt_param_names=opt_param)

        if "AccessPoint" in self.user_params:
            self.legacy_configure_ap_and_start()
        elif "OpenWrtAP" in self.user_params:
            self.configure_openwrt_ap_and_start(wpa_network=True)

        asserts.assert_true(
            len(self.reference_networks) > 0,
            "Need at least one reference network with psk.")
        self.network = self.reference_networks[0]["2g"]

    def setup_test(self):
        super().setup_test()
        self.dut.droid.wakeLockAcquireBright()
        self.dut.droid.wakeUpNow()
        wutils.wifi_toggle_state(self.dut, True)

    def teardown_test(self):
        super().teardown_test()
        self.dut.droid.wakeLockRelease()
        self.dut.droid.goToSleepNow()
        wutils.reset_wifi(self.dut)

    def teardown_class(self):
        if "AccessPoint" in self.user_params:
            del self.user_params["reference_networks"]

    """Helper Functions"""
    """Tests"""

    @test_tracker_info(uuid="b87fd23f-9bfc-406b-a5b2-17ce6be6c780")
    def test_wifi_framework_crash_reconnect(self):
        """Connect to a network, crash framework, then ensure
        we connect back to the previously connected network.

        Steps:
        1. Connect to a network.
        2. Restart framework.
        3. Reconnect to the previous network.

        """
        wutils.wifi_connect(self.dut, self.network, num_of_tries=3)
        # Restart framework
        self.log.info("Crashing framework")
        self.dut.restart_runtime()
        # We won't get the disconnect broadcast because framework crashed.
        # wutils.wait_for_disconnect(self.dut)
        time.sleep(RECOVERY_TIMEOUT)
        wifi_info = self.dut.droid.wifiGetConnectionInfo()
        if wifi_info[WifiEnums.SSID_KEY] != self.network[WifiEnums.SSID_KEY]:
            raise signals.TestFailure("Device did not connect to the"
                                      " network after crashing framework.")

    @test_tracker_info(uuid="33f9e4f6-29b8-4116-8f9b-5b13d93b4bcb")
    def test_wifi_cond_crash_reconnect(self):
        """Connect to a network, crash wificond, then ensure
        we connect back to the previously connected network.

        Steps:
        1. Connect to a network.
        2. Crash wificond.
        3. Ensure we get a disconnect.
        4. Ensure we reconnect to the previous network.

        """
        wutils.wifi_connect(self.dut, self.network, num_of_tries=3)
        # Restart wificond
        self.log.info("Crashing wificond")
        self.dut.adb.shell(WIFICOND_KILL_SHELL_COMMAND)
        wutils.wait_for_disconnect(self.dut)
        time.sleep(RECOVERY_TIMEOUT)
        wifi_info = self.dut.droid.wifiGetConnectionInfo()
        if wifi_info[WifiEnums.SSID_KEY] != self.network[WifiEnums.SSID_KEY]:
            raise signals.TestFailure("Device did not connect to the"
                                      " network after crashing wificond.")

    @test_tracker_info(uuid="463e3d7b-b0b7-4843-b83b-5613a71ae2ac")
    def test_wifi_vendorhal_crash_reconnect(self):
        """Connect to a network, crash wifi HAL, then ensure
        we connect back to the previously connected network.

        Steps:
        1. Connect to a network.
        2. Crash wifi HAL.
        3. Ensure we get a disconnect.
        4. Ensure we reconnect to the previous network.

        """
        wutils.wifi_connect(self.dut, self.network, num_of_tries=3)
        # Restart wificond
        self.log.info("Crashing wifi HAL")
        daemon_search_cmd = "ps -ef | grep %s" % WIFI_VENDOR_EXT_HAL_DAEMON_PREFIX
        result = self.dut.adb.shell(daemon_search_cmd) or ""
        if WIFI_VENDOR_EXT_HAL_DAEMON in result:
            self.log.info("Crashing wifi ext HAL")
            self.dut.adb.shell(WIFI_VENDOR_EXT_HAL_DAEMON_KILL_SHELL_COMMAND)
        else:
            self.log.info("Crashing wifi HAL")
            self.dut.adb.shell(WIFI_VENDOR_HAL_DAEMON_KILL_SHELL_COMMAND)
        wutils.wait_for_disconnect(self.dut)
        time.sleep(RECOVERY_TIMEOUT)
        wifi_info = self.dut.droid.wifiGetConnectionInfo()
        if wifi_info[WifiEnums.SSID_KEY] != self.network[WifiEnums.SSID_KEY]:
            raise signals.TestFailure("Device did not connect to the"
                                      " network after crashing wifi HAL.")

    @test_tracker_info(uuid="7c5cd1fc-8f8d-494c-beaf-4eb61b48917b")
    def test_wpa_supplicant_crash_reconnect(self):
        """Connect to a network, crash wpa_supplicant, then ensure
        we connect back to the previously connected network.

        Steps:
        1. Connect to a network.
        2. Crash wpa_supplicant.
        3. Ensure we get a disconnect.
        4. Ensure we reconnect to the previous network.

        """
        wutils.wifi_connect(self.dut, self.network, num_of_tries=3)
        # Restart wificond
        self.log.info("Crashing wpa_supplicant")
        self.dut.adb.shell(SUPPLICANT_KILL_SHELL_COMMAND)
        wutils.wait_for_disconnect(self.dut)
        time.sleep(RECOVERY_TIMEOUT)
        wifi_info = self.dut.droid.wifiGetConnectionInfo()
        if wifi_info[WifiEnums.SSID_KEY] != self.network[WifiEnums.SSID_KEY]:
            raise signals.TestFailure(
                "Device did not connect to the"
                " network after crashing wpa_supplicant.")
