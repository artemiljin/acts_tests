#!/usr/bin/env python3.4
#
#   Copyright 2022 - Google
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
"""
    Test Script for Telephony Pre Check In Sanity
"""

import collections
import random
import time
import os

from acts import signals
from acts.utils import rand_ascii_str
from acts.test_decorators import test_tracker_info
from acts_contrib.test_utils.tel.TelephonyBaseTest import TelephonyBaseTest
from acts_contrib.test_utils.tel.tel_defines import DIRECTION_MOBILE_ORIGINATED
from acts_contrib.test_utils.tel.tel_defines import DIRECTION_MOBILE_TERMINATED
from acts_contrib.test_utils.tel.tel_defines import DATA_STATE_CONNECTED
from acts_contrib.test_utils.tel.tel_defines import FAKE_DATE_TIME
from acts_contrib.test_utils.tel.tel_defines import FAKE_YEAR
from acts_contrib.test_utils.tel.tel_defines import GEN_2G
from acts_contrib.test_utils.tel.tel_defines import GEN_3G
from acts_contrib.test_utils.tel.tel_defines import GEN_4G
from acts_contrib.test_utils.tel.tel_defines import NETWORK_SERVICE_DATA
from acts_contrib.test_utils.tel.tel_defines import RAT_2G
from acts_contrib.test_utils.tel.tel_defines import RAT_3G
from acts_contrib.test_utils.tel.tel_defines import RAT_4G
from acts_contrib.test_utils.tel.tel_defines import SIM1_SLOT_INDEX
from acts_contrib.test_utils.tel.tel_defines import SIM2_SLOT_INDEX
from acts_contrib.test_utils.tel.tel_defines import MAX_WAIT_TIME_NW_SELECTION
from acts_contrib.test_utils.tel.tel_defines import MAX_WAIT_TIME_TETHERING_ENTITLEMENT_CHECK
from acts_contrib.test_utils.tel.tel_defines import TETHERING_MODE_WIFI
from acts_contrib.test_utils.tel.tel_defines import WAIT_TIME_ANDROID_STATE_SETTLING
from acts_contrib.test_utils.tel.tel_defines import WAIT_TIME_DATA_STATUS_CHANGE_DURING_WIFI_TETHERING
from acts_contrib.test_utils.tel.tel_defines import TETHERING_PASSWORD_HAS_ESCAPE
from acts_contrib.test_utils.tel.tel_defines import TETHERING_SPECIAL_SSID_LIST
from acts_contrib.test_utils.tel.tel_defines import TETHERING_SPECIAL_PASSWORD_LIST
from acts_contrib.test_utils.tel.tel_bt_utils import verify_bluetooth_tethering_connection
from acts_contrib.test_utils.tel.tel_data_utils import active_file_download_test
from acts_contrib.test_utils.tel.tel_data_utils import airplane_mode_test
from acts_contrib.test_utils.tel.tel_data_utils import browsing_test
from acts_contrib.test_utils.tel.tel_data_utils import get_mobile_data_usage
from acts_contrib.test_utils.tel.tel_data_utils import reboot_test
from acts_contrib.test_utils.tel.tel_data_utils import change_data_sim_and_verify_data
from acts_contrib.test_utils.tel.tel_data_utils import check_data_stall_detection
from acts_contrib.test_utils.tel.tel_data_utils import check_data_stall_recovery
from acts_contrib.test_utils.tel.tel_data_utils import check_network_validation_fail
from acts_contrib.test_utils.tel.tel_data_utils import data_connectivity_single_bearer
from acts_contrib.test_utils.tel.tel_data_utils import remove_mobile_data_usage_limit
from acts_contrib.test_utils.tel.tel_data_utils import set_mobile_data_usage_limit
from acts_contrib.test_utils.tel.tel_data_utils import tethering_check_internet_connection
from acts_contrib.test_utils.tel.tel_data_utils import test_data_connectivity_multi_bearer
from acts_contrib.test_utils.tel.tel_data_utils import test_setup_tethering
from acts_contrib.test_utils.tel.tel_data_utils import test_tethering_wifi_and_voice_call
from acts_contrib.test_utils.tel.tel_data_utils import test_wifi_connect_disconnect
from acts_contrib.test_utils.tel.tel_data_utils import wait_for_wifi_data_connection
from acts_contrib.test_utils.tel.tel_data_utils import wifi_cell_switching
from acts_contrib.test_utils.tel.tel_data_utils import wifi_tethering_cleanup
from acts_contrib.test_utils.tel.tel_data_utils import verify_toggle_apm_tethering_internet_connection
from acts_contrib.test_utils.tel.tel_data_utils import verify_tethering_entitlement_check
from acts_contrib.test_utils.tel.tel_data_utils import wifi_tethering_setup_teardown
from acts_contrib.test_utils.tel.tel_data_utils import test_wifi_tethering
from acts_contrib.test_utils.tel.tel_data_utils import test_start_wifi_tethering_connect_teardown
from acts_contrib.test_utils.tel.tel_data_utils import run_stress_test
from acts_contrib.test_utils.tel.tel_data_utils import verify_wifi_tethering_when_reboot
from acts_contrib.test_utils.tel.tel_data_utils import wait_and_verify_device_internet_connection
from acts_contrib.test_utils.tel.tel_data_utils import setup_device_internet_connection
from acts_contrib.test_utils.tel.tel_data_utils import setup_device_internet_connection_then_reboot
from acts_contrib.test_utils.tel.tel_data_utils import verify_internet_connection_in_doze_mode
from acts_contrib.test_utils.tel.tel_data_utils import verify_toggle_data_during_wifi_tethering
from acts_contrib.test_utils.tel.tel_subscription_utils import get_slot_index_from_subid
from acts_contrib.test_utils.tel.tel_subscription_utils import get_subid_from_slot_index
from acts_contrib.test_utils.tel.tel_subscription_utils import set_subid_for_data
from acts_contrib.test_utils.tel.tel_phone_setup_utils import phone_setup_3g
from acts_contrib.test_utils.tel.tel_phone_setup_utils import phone_setup_voice_3g
from acts_contrib.test_utils.tel.tel_phone_setup_utils import phone_setup_csfb
from acts_contrib.test_utils.tel.tel_phone_setup_utils import phone_setup_volte
from acts_contrib.test_utils.tel.tel_phone_setup_utils import phone_setup_4g
from acts_contrib.test_utils.tel.tel_phone_setup_utils import ensure_phones_default_state
from acts_contrib.test_utils.tel.tel_phone_setup_utils import ensure_network_generation
from acts_contrib.test_utils.tel.tel_phone_setup_utils import ensure_network_generation_for_subscription
from acts_contrib.test_utils.tel.tel_test_utils import toggle_airplane_mode_by_adb
from acts_contrib.test_utils.tel.tel_test_utils import verify_internet_connection
from acts_contrib.test_utils.tel.tel_test_utils import wait_for_data_attach_for_subscription
from acts_contrib.test_utils.tel.tel_test_utils import break_internet_except_sl4a_port
from acts_contrib.test_utils.tel.tel_test_utils import resume_internet_with_sl4a_port
from acts_contrib.test_utils.tel.tel_test_utils import get_device_epoch_time
from acts_contrib.test_utils.tel.tel_test_utils import test_data_browsing_success_using_sl4a
from acts_contrib.test_utils.tel.tel_test_utils import test_data_browsing_failure_using_sl4a
from acts_contrib.test_utils.tel.tel_test_utils import set_time_sync_from_network
from acts_contrib.test_utils.tel.tel_test_utils import datetime_handle
from acts_contrib.test_utils.tel.tel_voice_utils import call_setup_teardown
from acts_contrib.test_utils.tel.tel_voice_utils import hangup_call
from acts_contrib.test_utils.tel.tel_voice_utils import is_phone_in_call_3g
from acts_contrib.test_utils.tel.tel_voice_utils import is_phone_in_call_csfb
from acts_contrib.test_utils.tel.tel_voice_utils import is_phone_in_call_volte
from acts_contrib.test_utils.tel.tel_wifi_utils import WIFI_CONFIG_APBAND_2G
from acts_contrib.test_utils.tel.tel_wifi_utils import WIFI_CONFIG_APBAND_5G
from acts_contrib.test_utils.tel.tel_wifi_utils import ensure_wifi_connected
from acts_contrib.test_utils.tel.tel_wifi_utils import stop_wifi_tethering
from acts_contrib.test_utils.tel.tel_wifi_utils import wifi_reset
from acts_contrib.test_utils.tel.tel_wifi_utils import wifi_toggle_state


class TelLiveDataTest(TelephonyBaseTest):
    def setup_class(self):
        super().setup_class()

        self.stress_test_number = self.get_stress_test_number()
        self.provider = self.android_devices[0]
        self.clients = self.android_devices[1:]

    def setup_test(self):
        TelephonyBaseTest.setup_test(self)
        self.number_of_devices = 2

    def teardown_class(self):
        TelephonyBaseTest.teardown_class(self)


    """ Tests Begin """


    @test_tracker_info(uuid="ba24f9a3-0126-436c-8a5c-9f88859c273c")
    @TelephonyBaseTest.tel_test_wrap
    def test_data_browsing_for_single_phone(self):
        """ Browsing websites on cellular.

        Ensure phone attach, data on, WiFi off
        Verify 5 websites on cellular.

        Returns:
            True if pass; False if fail.
        """
        ad = self.android_devices[0]
        wifi_toggle_state(ad.log, ad, False)
        self.number_of_devices = 1

        for iteration in range(3):
            ad.log.info("Attempt %d", iteration + 1)
            if test_data_browsing_success_using_sl4a(ad.log, ad):
                ad.log.info("Data Browsing test PASS in iteration %d",
                            iteration + 1)
                return True
            time.sleep(WAIT_TIME_ANDROID_STATE_SETTLING)
        ad.log.info("Data Browsing test FAIL for all 3 iterations")
        return False


    @test_tracker_info(uuid="0679214b-9002-476d-83a7-3532b3cca209")
    @TelephonyBaseTest.tel_test_wrap
    def test_wifi_browsing_for_single_phone(self):
        """ Browsing websites on wifi.

        Ensure phone attach, data on, WiFi On, WiFi Connected.
        Verify 5 websites on WiFi.

        Returns:
            True if pass; False if fail.
        """
        ad = self.android_devices[0]
        wifi_toggle_state(ad.log, ad, True)
        self.number_of_devices = 1

        if not ensure_wifi_connected(ad.log, ad, self.wifi_network_ssid,
                                     self.wifi_network_pass):
            ad.log.error("WiFi connect fail.")
            return False
        for iteration in range(3):
            ad.log.info("Attempt %d", iteration + 1)
            if test_data_browsing_success_using_sl4a(ad.log, ad):
                ad.log.info("Data Browsing test PASS in iteration %d",
                            iteration + 1)
                wifi_toggle_state(ad.log, ad, False)
                return True
            time.sleep(WAIT_TIME_ANDROID_STATE_SETTLING)
        ad.log.info("Data Browsing test FAIL for all 3 iterations")
        wifi_toggle_state(ad.log, ad, False)
        return False


    @test_tracker_info(uuid="1b0354f3-8668-4a28-90a5-3b3d2b2756d3")
    @TelephonyBaseTest.tel_test_wrap
    def test_airplane_mode(self):
        """ Test airplane mode basic on Phone and Live SIM.

        Ensure phone attach, data on, WiFi off and verify Internet.
        Turn on airplane mode to make sure detach.
        Turn off airplane mode to make sure attach.
        Verify Internet connection.

        Returns:
            True if pass; False if fail.
        """
        self.number_of_devices = 1

        return airplane_mode_test(self.log, self.android_devices[0])

    @test_tracker_info(uuid="47430f01-583f-4efb-923a-285a51b75d50")
    @TelephonyBaseTest.tel_test_wrap
    def test_lte_wifi_switching(self):
        """Test data connection network switching when phone camped on LTE.

        Ensure phone is camped on LTE
        Ensure WiFi can connect to live network,
        Airplane mode is off, data connection is on, WiFi is on.
        Turn off WiFi, verify data is on cell and browse to google.com is OK.
        Turn on WiFi, verify data is on WiFi and browse to google.com is OK.
        Turn off WiFi, verify data is on cell and browse to google.com is OK.

        Returns:
            True if pass.
        """
        self.number_of_devices = 1

        return wifi_cell_switching(self.log, self.android_devices[0], GEN_4G,
                                   self.wifi_network_ssid,
                                   self.wifi_network_pass)

    @test_tracker_info(uuid="98d9f8c9-0532-49b6-85a3-5246b8314755")
    @TelephonyBaseTest.tel_test_wrap
    def test_lte_wifi_switching_stress(self):
        """LTE WiFi Switching Data Connection Check

        Same steps as test_lte_wifi_switching with stress testing

        Returns:
            True if pass.
        """
        MINIMUM_SUCCESS_RATE = .95
        success_count = 0
        fail_count = 0
        self.stress_test_number = 10
        self.number_of_devices = 1

        for i in range(1, self.stress_test_number + 1):
            ensure_phones_default_state(
                self.log, [self.android_devices[0]])

            if wifi_cell_switching(self.log, self.android_devices[0], GEN_4G,
                                   self.wifi_network_ssid,
                                   self.wifi_network_pass):
                success_count += 1
                result_str = "Succeeded"
            else:
                fail_count += 1
                result_str = "Failed"
            self.log.info("Iteration {} {}. Current: {} / {} passed.".format(
                i, result_str, success_count, self.stress_test_number))

        self.log.info("Final Count - Success: {}, Failure: {} - {}%".format(
            success_count, fail_count,
            str(100 * success_count / (success_count + fail_count))))
        if success_count / (
                success_count + fail_count) >= MINIMUM_SUCCESS_RATE:
            return True
        else:
            return False

    @test_tracker_info(uuid="8a836cf1-600b-4cf3-abfe-2e3da5c11396")
    @TelephonyBaseTest.tel_test_wrap
    def test_wcdma_wifi_switching(self):
        """Test data connection network switching when phone camped on WCDMA.

        Ensure phone is camped on WCDMA
        Ensure WiFi can connect to live network,
        Airplane mode is off, data connection is on, WiFi is on.
        Turn off WiFi, verify data is on cell and browse to google.com is OK.
        Turn on WiFi, verify data is on WiFi and browse to google.com is OK.
        Turn off WiFi, verify data is on cell and browse to google.com is OK.

        Returns:
            True if pass.
        """
        self.number_of_devices = 1

        return wifi_cell_switching(self.log, self.android_devices[0], GEN_3G,
                                   self.wifi_network_ssid,
                                   self.wifi_network_pass)

    @test_tracker_info(uuid="c016f2e8-0af6-42e4-a3cb-a2b7d8b564d0")
    @TelephonyBaseTest.tel_test_wrap
    def test_gsm_wifi_switching(self):
        """Test data connection network switching when phone camped on GSM.

        Ensure phone is camped on GSM
        Ensure WiFi can connect to live network,,
        Airplane mode is off, data connection is on, WiFi is on.
        Turn off WiFi, verify data is on cell and browse to google.com is OK.
        Turn on WiFi, verify data is on WiFi and browse to google.com is OK.
        Turn off WiFi, verify data is on cell and browse to google.com is OK.

        Returns:
            True if pass.
        """
        self.number_of_devices = 1

        return wifi_cell_switching(self.log, self.android_devices[0], GEN_2G,
                                   self.wifi_network_ssid,
                                   self.wifi_network_pass)

    @test_tracker_info(uuid="78d6b258-82d4-47b4-8723-3b3a15412d2d")
    @TelephonyBaseTest.tel_test_wrap
    def test_lte_multi_bearer(self):
        """Test LTE data connection before call and in call. (VoLTE call)


        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in LTE, verify Internet.
        Initiate a voice call. verify Internet.
        Disable Cellular Data, verify Internet is inaccessible.
        Enable Cellular Data, verify Internet.
        Hangup Voice Call, verify Internet.

        Returns:
            True if success.
            False if failed.
        """
        self.number_of_devices = 1

        return test_data_connectivity_multi_bearer(
            self.log, self.android_devices, 'volte')

    @test_tracker_info(uuid="5c9cb076-0c26-4517-95dc-2ec4974e8ce3")
    @TelephonyBaseTest.tel_test_wrap
    def test_wcdma_multi_bearer(self):
        """Test WCDMA data connection before call and in call.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in WCDMA, verify Internet.
        Initiate a voice call. verify Internet.
        Disable Cellular Data, verify Internet is inaccessible.
        Enable Cellular Data, verify Internet.
        Hangup Voice Call, verify Internet.

        Returns:
            True if success.
            False if failed.
        """

        return test_data_connectivity_multi_bearer(
            self.log, self.android_devices, '3g')

    @test_tracker_info(uuid="314bbf1c-073f-4d48-9817-a6e14f96f3c0")
    @TelephonyBaseTest.tel_test_wrap
    def test_gsm_multi_bearer_mo(self):
        """Test gsm data connection before call and in call.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in GSM, verify Internet.
        Initiate a MO voice call. Verify there is no Internet during call.
        Hangup Voice Call, verify Internet.

        Returns:
            True if success.
            False if failed.
        """

        return test_data_connectivity_multi_bearer(self.log,
            self.android_devices, '2g', False, DIRECTION_MOBILE_ORIGINATED)

    @test_tracker_info(uuid="549271ff-1034-4d02-8d92-b9d1b2bb912e")
    @TelephonyBaseTest.tel_test_wrap
    def test_gsm_multi_bearer_mt(self):
        """Test gsm data connection before call and in call.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in GSM, verify Internet.
        Initiate a MT voice call. Verify there is no Internet during call.
        Hangup Voice Call, verify Internet.

        Returns:
            True if success.
            False if failed.
        """

        return test_data_connectivity_multi_bearer(self.log,
            self.android_devices, '2g', False, DIRECTION_MOBILE_TERMINATED)

    @test_tracker_info(uuid="111de471-559a-4bc3-9d3e-de18f098c162")
    @TelephonyBaseTest.tel_test_wrap
    def test_wcdma_multi_bearer_stress(self):
        """Stress Test WCDMA data connection before call and in call.

        This is a stress test for "test_wcdma_multi_bearer".
        Default MINIMUM_SUCCESS_RATE is set to 95%.

        Returns:
            True stress pass rate is higher than MINIMUM_SUCCESS_RATE.
            False otherwise.
        """
        MINIMUM_SUCCESS_RATE = .95
        success_count = 0
        fail_count = 0

        for i in range(1, self.stress_test_number + 1):

            ensure_phones_default_state(
                self.log, [self.android_devices[0], self.android_devices[1]])

            if self.test_wcdma_multi_bearer():
                success_count += 1
                result_str = "Succeeded"
            else:
                fail_count += 1
                result_str = "Failed"
            self.log.info("Iteration {} {}. Current: {} / {} passed.".format(
                i, result_str, success_count, self.stress_test_number))

        self.log.info("Final Count - Success: {}, Failure: {} - {}%".format(
            success_count, fail_count,
            str(100 * success_count / (success_count + fail_count))))
        if success_count / (
                success_count + fail_count) >= MINIMUM_SUCCESS_RATE:
            return True
        else:
            return False

    @test_tracker_info(uuid="c7f14ba7-7ac3-45d2-b391-5ed5c4b0e70b")
    @TelephonyBaseTest.tel_test_wrap
    def test_lte_multi_bearer_stress(self):
        """Stress Test LTE data connection before call and in call. (VoLTE call)

        This is a stress test for "test_lte_multi_bearer".
        Default MINIMUM_SUCCESS_RATE is set to 95%.

        Returns:
            True stress pass rate is higher than MINIMUM_SUCCESS_RATE.
            False otherwise.
        """
        ads = self.android_devices
        MINIMUM_SUCCESS_RATE = .95
        success_count = 0
        fail_count = 0

        for i in range(1, self.stress_test_number + 1):

            ensure_phones_default_state(
                self.log, [self.android_devices[0], self.android_devices[1]])

            if self.test_lte_multi_bearer():
                success_count += 1
                result_str = "Succeeded"
            else:
                fail_count += 1
                result_str = "Failed"
            self.log.info("Iteration {} {}. Current: {} / {} passed.".format(
                i, result_str, success_count, self.stress_test_number))

        self.log.info("Final Count - Success: {}, Failure: {} - {}%".format(
            success_count, fail_count,
            str(100 * success_count / (success_count + fail_count))))
        if success_count / (
                success_count + fail_count) >= MINIMUM_SUCCESS_RATE:
            return True
        else:
            return False


    @test_tracker_info(uuid="dcb9bdc6-dbe2-47e1-9c2d-6f37c529d366")
    @TelephonyBaseTest.tel_test_wrap
    def test_2g_data_connectivity(self):
        """Test data connection in 2G.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Ensure phone data generation is 2G.
        Verify Internet.
        Disable Cellular Data, verify Internet is inaccessible.
        Enable Cellular Data, verify Internet.

        Returns:
            True if success.
            False if failed.
        """
        self.number_of_devices = 1

        wifi_reset(self.log, self.android_devices[0])
        wifi_toggle_state(self.log, self.android_devices[0], False)
        return data_connectivity_single_bearer(self.log,
                                               self.android_devices[0], RAT_2G)

    @test_tracker_info(uuid="84197a49-d73f-44ce-8b9e-9479e5c4dfdc")
    @TelephonyBaseTest.tel_test_wrap
    def test_2g_wifi_not_associated(self):
        """Test data connection in 2G.

        Turn off airplane mode, enable WiFi (but not connected), enable Cellular Data.
        Ensure phone data generation is 2G.
        Verify Internet.
        Disable Cellular Data, verify Internet is inaccessible.
        Enable Cellular Data, verify Internet.

        Returns:
            True if success.
            False if failed.
        """
        self.number_of_devices = 1

        wifi_reset(self.log, self.android_devices[0])
        wifi_toggle_state(self.log, self.android_devices[0], False)
        wifi_toggle_state(self.log, self.android_devices[0], True)
        return data_connectivity_single_bearer(self.log,
                                               self.android_devices[0], RAT_2G)

    @test_tracker_info(uuid="97067ebb-130a-4fcb-8e6b-f4ec5874828f")
    @TelephonyBaseTest.tel_test_wrap
    def test_3g_data_connectivity(self):
        """Test data connection in 3G.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Ensure phone data generation is 3G.
        Verify Internet.
        Disable Cellular Data, verify Internet is inaccessible.
        Enable Cellular Data, verify Internet.

        Returns:
            True if success.
            False if failed.
        """
        self.number_of_devices = 1

        wifi_reset(self.log, self.android_devices[0])
        wifi_toggle_state(self.log, self.android_devices[0], False)
        return data_connectivity_single_bearer(self.log,
                                               self.android_devices[0], RAT_3G)

    @test_tracker_info(uuid="ffe2a392-95b8-4a4d-8a6f-bfa846c3462f")
    @TelephonyBaseTest.tel_test_wrap
    def test_3g_wifi_not_associated(self):
        """Test data connection in 3G.

        Turn off airplane mode, enable WiFi (but not connected), enable Cellular Data.
        Ensure phone data generation is 3G.
        Verify Internet.
        Disable Cellular Data, verify Internet is inaccessible.
        Enable Cellular Data, verify Internet.

        Returns:
            True if success.
            False if failed.
        """
        self.number_of_devices = 1

        wifi_reset(self.log, self.android_devices[0])
        wifi_toggle_state(self.log, self.android_devices[0], False)
        wifi_toggle_state(self.log, self.android_devices[0], True)
        return data_connectivity_single_bearer(self.log,
                                               self.android_devices[0], RAT_3G)

    @test_tracker_info(uuid="9c2f459f-1aac-4c68-818b-8698e8124c8b")
    @TelephonyBaseTest.tel_test_wrap
    def test_4g_data_connectivity(self):
        """Test data connection in 4g.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Ensure phone data generation is 4g.
        Verify Internet.
        Disable Cellular Data, verify Internet is inaccessible.
        Enable Cellular Data, verify Internet.

        Returns:
            True if success.
            False if failed.
        """
        self.number_of_devices = 1

        wifi_reset(self.log, self.android_devices[0])
        wifi_toggle_state(self.log, self.android_devices[0], False)
        return data_connectivity_single_bearer(self.log,
                                               self.android_devices[0], RAT_4G)

    @test_tracker_info(uuid="015a39a1-15ac-4b76-962b-d7d82d52d425")
    @TelephonyBaseTest.tel_test_wrap
    def test_4g_wifi_not_associated(self):
        """Test data connection in 4g.

        Turn off airplane mode, enable WiFi (but not connected), enable Cellular Data.
        Ensure phone data generation is 4g.
        Verify Internet.
        Disable Cellular Data, verify Internet is inaccessible.
        Enable Cellular Data, verify Internet.

        Returns:
            True if success.
            False if failed.
        """
        self.number_of_devices = 1

        wifi_reset(self.log, self.android_devices[0])
        wifi_toggle_state(self.log, self.android_devices[0], False)
        wifi_toggle_state(self.log, self.android_devices[0], True)
        return data_connectivity_single_bearer(self.log,
                                               self.android_devices[0], RAT_4G)

    @test_tracker_info(uuid="44f47b64-f8bc-4a17-9195-42dcca0806bb")
    @TelephonyBaseTest.tel_test_wrap
    def test_3g_data_connectivity_stress(self):
        """Stress Test data connection in 3G.

        This is a stress test for "test_3g".
        Default MINIMUM_SUCCESS_RATE is set to 95%.

        Returns:
            True stress pass rate is higher than MINIMUM_SUCCESS_RATE.
            False otherwise.
        """
        MINIMUM_SUCCESS_RATE = .95
        success_count = 0
        fail_count = 0
        self.number_of_devices = 1

        for i in range(1, self.stress_test_number + 1):

            ensure_phones_default_state(self.log, [self.android_devices[0]])
            wifi_reset(self.log, self.android_devices[0])
            wifi_toggle_state(self.log, self.android_devices[0], False)

            if data_connectivity_single_bearer(
                    self.log, self.android_devices[0], RAT_3G):
                success_count += 1
                result_str = "Succeeded"
            else:
                fail_count += 1
                result_str = "Failed"
            self.log.info("Iteration {} {}. Current: {} / {} passed.".format(
                i, result_str, success_count, self.stress_test_number))

        self.log.info("Final Count - Success: {}, Failure: {} - {}%".format(
            success_count, fail_count,
            str(100 * success_count / (success_count + fail_count))))
        if success_count / (
                success_count + fail_count) >= MINIMUM_SUCCESS_RATE:
            return True
        else:
            return False

    @test_tracker_info(uuid="c8876388-0441-4a51-81e6-ac2cb358a531")
    @TelephonyBaseTest.tel_test_wrap
    def test_4g_data_connectivity_stress(self):
        """Stress Test data connection in 4g.

        This is a stress test for "test_4g".
        Default MINIMUM_SUCCESS_RATE is set to 95%.

        Returns:
            True stress pass rate is higher than MINIMUM_SUCCESS_RATE.
            False otherwise.
        """
        MINIMUM_SUCCESS_RATE = .95
        success_count = 0
        fail_count = 0
        self.number_of_devices = 1

        for i in range(1, self.stress_test_number + 1):

            ensure_phones_default_state(self.log, [self.android_devices[0]])
            wifi_reset(self.log, self.android_devices[0])
            wifi_toggle_state(self.log, self.android_devices[0], False)

            if data_connectivity_single_bearer(
                    self.log, self.android_devices[0], RAT_4G):
                success_count += 1
                result_str = "Succeeded"
            else:
                fail_count += 1
                result_str = "Failed"
            self.log.info("Iteration {} {}. Current: {} / {} passed.".format(
                i, result_str, success_count, self.stress_test_number))

        self.log.info("Final Count - Success: {}, Failure: {} - {}%".format(
            success_count, fail_count,
            str(100 * success_count / (success_count + fail_count))))
        if success_count / (
                success_count + fail_count) >= MINIMUM_SUCCESS_RATE:
            return True
        else:
            return False


    @test_tracker_info(uuid="2d945656-22f7-4610-9a84-40ce04d603a4")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_4g_to_bluetooth(self):
        """Bluetooth Tethering test: LTE to Bluetooth Tethering

        1. DUT in LTE mode, idle.
        2. DUT start Bluetooth Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB
        5. Toggle provider bluetooth connection
        6. Verify Internet access on DUT and PhoneB

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_4G):
            self.log.error("Verify 4G Internet access failed.")
            return False

        return verify_bluetooth_tethering_connection(self.log, self.provider, self.clients)

    @test_tracker_info(uuid="8d2ae56b-c2c1-4c32-9b8e-5044007b5b90")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_4g_to_bluetooth_with_voice_call(self):
        """Bluetooth Tethering test: LTE to Bluetooth Tethering

        1. DUT in LTE mode, idle.
        2. DUT start Bluetooth Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB
        5. Verify provider and client are able to make or receive phone call
        6. Verify Internet access on DUT and PhoneB

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_4G):
            self.log.error("Verify 4G Internet access failed.")
            return False

        return verify_bluetooth_tethering_connection(self.log, self.provider, self.clients,
            toggle_tethering=False, toggle_bluetooth=False, voice_call=True)

    @test_tracker_info(uuid="b4617727-fa83-4451-89d7-7e574c0a0938")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_4g_to_bluetooth_toggle_data(self):
        """Bluetooth Tethering test: LTE to Bluetooth Tethering

        1. DUT in LTE mode, idle.
        2. DUT start Bluetooth Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB
        5. Toggle provider data connection
        6. Verify Internet access on DUT and PhoneB

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_4G):
            self.log.error("Verify 4G Internet access failed.")
            return False

        return verify_bluetooth_tethering_connection(self.log, self.provider, self.clients,
            toggle_tethering=False, toggle_bluetooth=False, toggle_data=True)

    @test_tracker_info(uuid="6a0f6001-609d-41f2-ad09-c8ae19f73ac8")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_4g_to_bluetooth_toggle_tethering(self):
        """Bluetooth Tethering test: LTE to Bluetooth Tethering

        1. DUT in LTE mode, idle.
        2. DUT start Bluetooth Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB
        5. Toggle provider bluetooth tethering
        6. Verify Internet access on DUT and PhoneB

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_4G):
            self.log.error("Verify 4G Internet access failed.")
            return False

        return verify_bluetooth_tethering_connection(self.log, self.provider, self.clients,
            toggle_tethering=True, toggle_bluetooth=False, toggle_data=False)

    @test_tracker_info(uuid="b1abc1ac-8018-4956-a17e-bf2ceaf264ea")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_3g_to_bluetooth(self):
        """Bluetooth Tethering test: 3G to Bluetoothing Tethering

        1. DUT in 3G mode, idle.
        2. DUT start bluetooth Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB
        5. Toggle provider bluetooth connection
        6. Verify Internet access on DUT and PhoneB

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_3G):
            self.log.error("Verify 3G Internet access failed.")
            return False

        return verify_bluetooth_tethering_connection(self.log, self.provider, self.clients)

    @test_tracker_info(uuid="69793745-0c49-4cef-9879-d372e3a3f4c7")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_3g_to_bluetooth_with_voice_call(self):
        """Bluetooth Tethering test: 3G to Bluetooth Tethering

        1. DUT in 3G mode, idle.
        2. DUT start Bluetooth Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB
        5. Verify provider and client are able to make or receive phone call
        6. Verify Internet access on DUT and PhoneB

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_3G):
            self.log.error("Verify 3G Internet access failed.")
            return False

        return verify_bluetooth_tethering_connection(self.log, self.provider, self.clients,
            toggle_tethering=False, toggle_bluetooth=False, voice_call=True)

    @test_tracker_info(uuid="4275ee69-dfdf-4f47-82c5-4224fceee761")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_3g_to_bluetooth_toggle_data(self):
        """Bluetooth Tethering test: 3G to Bluetoothing Tethering

        1. DUT in 3G mode, idle.
        2. DUT start bluetooth Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB
        5. Toggle provider data connection
        6. Verify Internet access on DUT and PhoneB

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_3G):
            self.log.error("Verify 3G Internet access failed.")
            return False

        return verify_bluetooth_tethering_connection(self.log, self.provider, self.clients,
            toggle_tethering=False, toggle_bluetooth=False, toggle_data=True)

    @test_tracker_info(uuid="db0e0f27-1a4f-4301-832d-b66415e289f3")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_2g_to_bluetooth(self):
        """Bluetooth Tethering test: 2G to Bluetooth Tethering

        1. DUT in 2G mode, idle.
        2. DUT start bluetooth Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB
        5. Toggle provider bluetooth connection
        6. Verify Internet access on DUT and PhoneB

        Returns:
            True if success.
            False if failed.
        """
        for a in self.android_devices:
            a.adb.shell("setprop persist.bluetooth.btsnoopenable true")
            if not toggle_airplane_mode_by_adb(self.log, a, True):
                self.log.error("Failed to toggle airplane mode on")
                return False
            if not toggle_airplane_mode_by_adb(self.log, a, False):
                self.log.error("Failed to toggle airplane mode off")
                return False

        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_2G):
            self.log.error("Verify 3G Internet access failed.")
            return False

        return verify_bluetooth_tethering_connection(self.log, self.provider, self.clients)

    @test_tracker_info(uuid="584e9fa5-a38e-47cd-aa33-fcf8d72c423e")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_2g_to_bluetooth_with_voice_call(self):
        """Bluetooth Tethering test: 2G to Bluetooth Tethering

        1. DUT in 2G mode, idle.
        2. DUT start Bluetooth Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB
        5. Verify provider and client are able to make or receive phone call
        6. Verify Internet access on DUT and PhoneB

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_2G):
            self.log.error("Verify 2G Internet access failed.")
            return False

        return verify_bluetooth_tethering_connection(self.log, self.provider, self.clients,
            toggle_tethering=False, toggle_bluetooth=False, voice_call=True)

    @test_tracker_info(uuid="be3e74f9-3dc8-4b72-8a33-32bff0868a44")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_2g_to_bluetooth_toggle_data(self):
        """Bluetooth Tethering test: 2G to Bluetooth Tethering

        1. DUT in 2G mode, idle.
        2. DUT start Bluetooth Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB
        5. Toggle provider data connection
        6. Verify Internet access on DUT and PhoneB

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_2G):
            self.log.error("Verify 4G Internet access failed.")
            return False

        return verify_bluetooth_tethering_connection(self.log, self.provider, self.clients,
            toggle_tethering=False, toggle_bluetooth=False, toggle_data=True)

    @test_tracker_info(uuid="4a106549-0bfa-4c8f-8e66-edec93fabadf")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_rat_from_4g_to_3g_bluetooth(self):
        """Bluetooth Tethering test: 2G to Bluetooth Tethering

        1. DUT in 4G mode, idle.
        2. DUT start bluetooth Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB
        5. Change provider RAT to 3G
        6. Verify Internet access on DUT and PhoneB

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_4G):
            self.log.error("Verify 3G Internet access failed.")
            return False

        return verify_bluetooth_tethering_connection(self.log, self.provider, self.clients,
            toggle_tethering=False,
            toggle_bluetooth=False,
            toggle_data=False,
            change_rat=RAT_3G)

    @test_tracker_info(uuid="eaa5b61b-f054-437f-ae82-8d80f6487785")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_rat_from_4g_to_2g_bluetooth(self):
        """Bluetooth Tethering test: 2G to Bluetooth Tethering

        1. DUT in 4G mode, idle.
        2. DUT start bluetooth Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB
        5. Change provider RAT to 2G
        6. Verify Internet access on DUT and PhoneB

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_4G):
            self.log.error("Verify 3G Internet access failed.")
            return False

        return verify_bluetooth_tethering_connection(self.log, self.provider, self.clients,
            toggle_tethering=False,
            toggle_bluetooth=False,
            toggle_data=False,
            change_rat=RAT_2G)

    @test_tracker_info(uuid="912a11a3-14b3-4928-885f-cea69f14a571")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_4g_to_2gwifi(self):
        """WiFi Tethering test: LTE to WiFI 2.4G Tethering

        1. DUT in LTE mode, idle.
        2. DUT start 2.4G WiFi Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_4G):
            self.log.error("Verify 4G Internet access failed.")
            return False

        return wifi_tethering_setup_teardown(
            self.log,
            self.provider,
            self.clients,
            ap_band=WIFI_CONFIG_APBAND_2G,
            check_interval=10,
            check_iteration=10)

    @test_tracker_info(uuid="743e3998-d39f-42b9-b11f-009dcee34f3f")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_4g_to_5gwifi(self):
        """WiFi Tethering test: LTE to WiFI 5G Tethering

        1. DUT in LTE mode, idle.
        2. DUT start 5G WiFi Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_4G):
            self.log.error("Verify 4G Internet access failed.")
            return False

        return wifi_tethering_setup_teardown(
            self.log,
            self.provider,
            self.clients,
            ap_band=WIFI_CONFIG_APBAND_5G,
            check_interval=10,
            check_iteration=10)


    @test_tracker_info(uuid="c1a16464-3800-40d3-ba63-35db784e0383")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_default_to_5gwifi(self):
        """WiFi Tethering test: Default to WiFI 5G Tethering

        1. DUT in default mode, idle.
        2. DUT start 5G WiFi Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB
        5. True: Stop
           False: Change DUT to next device and repeat until find the device
                  with tethering capability

        Returns:
            True if success.
            False if no device has tethering capability.
        """
        num = len(self.android_devices)
        for idx, ad in enumerate(self.android_devices):
            self.provider = self.android_devices[idx]
            self.clients = self.android_devices[:
                                                idx] + self.android_devices[idx
                                                                            +
                                                                            1:]
            ensure_phones_default_state(self.log, self.android_devices)
            wifi_toggle_state(self.log, self.provider, False)

            if not test_setup_tethering(self.log, self.provider, self.clients, None):
                self.provider.log.error("Data connection check failed.")
                continue

            if not self.provider.droid.carrierConfigIsTetheringModeAllowed(
                    TETHERING_MODE_WIFI,
                    MAX_WAIT_TIME_TETHERING_ENTITLEMENT_CHECK):
                self.provider.log.info("Tethering is not entitled")
                continue

            if wifi_tethering_setup_teardown(
                    self.log,
                    self.provider, [self.clients[0]],
                    ap_band=WIFI_CONFIG_APBAND_5G,
                    check_interval=10,
                    check_iteration=10):
                self.android_devices = [self.provider] + self.clients
                return True
            elif idx == num - 1:
                self.log.error("Tethering is not working on all devices")
                return False
        self.log.error(
            "Failed to enable tethering on any device in this testbed")
        raise signals.TestAbortClass(
            "Tethering is not available on all devices in this testbed")

    @test_tracker_info(uuid="c9a570b0-838c-44ba-991c-f1ddeee21f3c")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_default_to_2gwifi(self):
        """WiFi Tethering test: Default to WiFI 2G Tethering

        1. DUT in default mode, idle.
        2. DUT start 2G WiFi Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB
        5. True: Stop
           False: Change DUT to next device and repeat until find the device
                  with tethering capability

        Returns:
            True if success.
            False if no device has tethering capability.
        """
        num = len(self.android_devices)
        for idx, ad in enumerate(self.android_devices):
            self.provider = self.android_devices[idx]
            self.clients = self.android_devices[:
                                                idx] + self.android_devices[idx
                                                                            +
                                                                            1:]
            ensure_phones_default_state(self.log, self.android_devices)
            wifi_toggle_state(self.log, self.provider, False)

            if not test_setup_tethering(self.log, self.provider, self.clients, None):
                self.provider.log.error("Data connection check failed.")
                continue

            if not self.provider.droid.carrierConfigIsTetheringModeAllowed(
                    TETHERING_MODE_WIFI,
                    MAX_WAIT_TIME_TETHERING_ENTITLEMENT_CHECK):
                self.provider.log.info("Tethering is not entitled")
                continue

            if wifi_tethering_setup_teardown(
                    self.log,
                    self.provider, [self.clients[0]],
                    ap_band=WIFI_CONFIG_APBAND_2G,
                    check_interval=10,
                    check_iteration=10):
                self.android_devices = [self.provider] + self.clients
                return True
            elif idx == num - 1:
                self.log.error("Tethering is not working on all devices")
                return False
        self.log.error(
            "Failed to enable tethering on any device in this testbed")
        raise signals.TestAbortClass(
            "Tethering is not available on all devices in this testbed")

    @test_tracker_info(uuid="59be8d68-f05b-4448-8584-de971174fd81")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_3g_to_2gwifi(self):
        """WiFi Tethering test: 3G to WiFI 2.4G Tethering

        1. DUT in 3G mode, idle.
        2. DUT start 2.4G WiFi Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_3G):
            self.log.error("Verify 3G Internet access failed.")
            return False

        return wifi_tethering_setup_teardown(
            self.log,
            self.provider,
            self.clients,
            ap_band=WIFI_CONFIG_APBAND_2G,
            check_interval=10,
            check_iteration=10)

    @test_tracker_info(uuid="1be6b741-92e8-4ee1-9f59-e7f9f369b065")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_3g_to_5gwifi(self):
        """WiFi Tethering test: 3G to WiFI 5G Tethering

        1. DUT in 3G mode, idle.
        2. DUT start 5G WiFi Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_3G):
            self.log.error("Verify 3G Internet access failed.")
            return False

        return wifi_tethering_setup_teardown(
            self.log,
            self.provider,
            self.clients,
            ap_band=WIFI_CONFIG_APBAND_5G,
            check_interval=10,
            check_iteration=10)

    @test_tracker_info(uuid="89fe6321-4c0d-40c0-89b2-54008ecca68f")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_2g_to_2gwifi(self):
        """WiFi Tethering test: 2G to WiFI 2.4G Tethering

        1. DUT in 2G mode, idle.
        2. DUT start 2.4G WiFi Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_2G):
            self.log.error("Verify 2G Internet access failed.")
            return False

        return wifi_tethering_setup_teardown(
            self.log,
            self.provider, [self.clients[0]],
            ap_band=WIFI_CONFIG_APBAND_2G,
            check_interval=10,
            check_iteration=10)

    @test_tracker_info(uuid="b8258d51-9581-4d52-80b6-501941ec1191")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_2g_to_5gwifi(self):
        """WiFi Tethering test: 2G to WiFI 5G Tethering

        1. DUT in 2G mode, idle.
        2. DUT start 5G WiFi Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_2G):
            self.log.error("Verify 2G Internet access failed.")
            return False

        return wifi_tethering_setup_teardown(
            self.log,
            self.provider, [self.clients[0]],
            ap_band=WIFI_CONFIG_APBAND_5G,
            check_interval=10,
            check_iteration=10)

    @test_tracker_info(uuid="8ed766a6-71c5-4b3b-8897-a4e796c75619")
    @TelephonyBaseTest.tel_test_wrap
    def test_disable_wifi_tethering_resume_connected_wifi(self):
        """WiFi Tethering test: WiFI connected to 2.4G network,
        start (LTE) 2.4G WiFi tethering, then stop tethering

        1. DUT in data connected, idle. WiFi connected to 2.4G Network
        2. DUT start 2.4G WiFi Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB
        5. Disable WiFi Tethering on DUT.
        6. Verify DUT automatically connect to previous WiFI network

        Returns:
            True if success.
            False if failed.
        """
        # Ensure provider connecting to wifi network.
        def setup_provider_internet_connection():
            return setup_device_internet_connection(self.log,
                                                    self.provider,
                                                    self.wifi_network_ssid,
                                                    self.wifi_network_pass)

        if not test_wifi_tethering(self.log,
                                   self.provider,
                                   self.clients,
                                   [self.clients[0]],
                                   None,
                                   WIFI_CONFIG_APBAND_2G,
                                   check_interval=10,
                                   check_iteration=2,
                                   pre_teardown_func=setup_provider_internet_connection):
            return False

        if not wait_and_verify_device_internet_connection(self.log, self.provider):
            return False
        return True

    @test_tracker_info(uuid="b879ceb2-1b80-4762-93f9-afef4d688c28")
    @TelephonyBaseTest.tel_test_wrap
    def test_toggle_data_during_active_wifi_tethering(self):
        """WiFi Tethering test: Toggle Data during active WiFi Tethering

        1. DUT data connection is on and idle.
        2. DUT start 2.4G WiFi Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB
        5. Disable Data on DUT, verify PhoneB still connected to WiFi, but no Internet access.
        6. Enable Data on DUT, verify PhoneB still connected to WiFi and have Internet access.

        Returns:
            True if success.
            False if failed.
        """
        if not verify_toggle_data_during_wifi_tethering(self.log,
                                                        self.provider,
                                                        self.clients):
            return False
        return True

    # Invalid Live Test. Can't rely on the result of this test with live network.
    # Network may decide not to change the RAT when data conenction is active.
    @test_tracker_info(uuid="c92a961b-e85d-435c-8988-052928add591")
    @TelephonyBaseTest.tel_test_wrap
    def test_change_rat_during_active_wifi_tethering_lte_to_3g(self):
        """WiFi Tethering test: Change Cellular Data RAT generation from LTE to 3G,
            during active WiFi Tethering.

        1. DUT in LTE mode, idle.
        2. DUT start 2.4G WiFi Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verily Internet access on DUT and PhoneB
        5. Change DUT Cellular Data RAT generation from LTE to 3G.
        6. Verify both DUT and PhoneB have Internet access.

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_4G):
            self.log.error("Verify 4G Internet access failed.")
            return False
        try:
            if not wifi_tethering_setup_teardown(
                    self.log,
                    self.provider, [self.clients[0]],
                    ap_band=WIFI_CONFIG_APBAND_2G,
                    check_interval=10,
                    check_iteration=2,
                    do_cleanup=False):
                self.log.error("WiFi Tethering failed.")
                return False

            if not self.provider.droid.wifiIsApEnabled():
                self.provider.log.error("Provider WiFi tethering stopped.")
                return False

            self.log.info("Provider change RAT from LTE to 3G.")
            if not ensure_network_generation(
                    self.log,
                    self.provider,
                    RAT_3G,
                    voice_or_data=NETWORK_SERVICE_DATA,
                    toggle_apm_after_setting=False):
                self.provider.log.error("Provider failed to reselect to 3G.")
                return False
            time.sleep(WAIT_TIME_DATA_STATUS_CHANGE_DURING_WIFI_TETHERING)
            if not verify_internet_connection(self.log, self.provider):
                self.provider.log.error("Data not available on Provider.")
                return False
            if not self.provider.droid.wifiIsApEnabled():
                self.provider.log.error("Provider WiFi tethering stopped.")
                return False
            if not tethering_check_internet_connection(
                    self.log, self.provider, [self.clients[0]], 10, 5):
                return False
        finally:
            if not wifi_tethering_cleanup(self.log, self.provider,
                                          self.clients):
                return False
        return True

    # Invalid Live Test. Can't rely on the result of this test with live network.
    # Network may decide not to change the RAT when data conenction is active.
    @test_tracker_info(uuid="eb5f0180-b70d-436f-8fcb-60c59307cc43")
    @TelephonyBaseTest.tel_test_wrap
    def test_change_rat_during_active_wifi_tethering_3g_to_lte(self):
        """WiFi Tethering test: Change Cellular Data RAT generation from 3G to LTE,
            during active WiFi Tethering.

        1. DUT in 3G mode, idle.
        2. DUT start 2.4G WiFi Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verily Internet access on DUT and PhoneB
        5. Change DUT Cellular Data RAT generation from 3G to LTE.
        6. Verify both DUT and PhoneB have Internet access.

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_3G):
            self.log.error("Verify 3G Internet access failed.")
            return False
        try:
            if not wifi_tethering_setup_teardown(
                    self.log,
                    self.provider, [self.clients[0]],
                    ap_band=WIFI_CONFIG_APBAND_2G,
                    check_interval=10,
                    check_iteration=2,
                    do_cleanup=False):
                self.log.error("WiFi Tethering failed.")
                return False

            if not self.provider.droid.wifiIsApEnabled():
                self.log.error("Provider WiFi tethering stopped.")
                return False

            self.log.info("Provider change RAT from 3G to 4G.")
            if not ensure_network_generation(
                    self.log,
                    self.provider,
                    RAT_4G,
                    voice_or_data=NETWORK_SERVICE_DATA,
                    toggle_apm_after_setting=False):
                self.log.error("Provider failed to reselect to 4G.")
                return False
            time.sleep(WAIT_TIME_DATA_STATUS_CHANGE_DURING_WIFI_TETHERING)
            if not verify_internet_connection(self.log, self.provider):
                self.provider.log.error("Data not available on Provider.")
                return False
            if not self.provider.droid.wifiIsApEnabled():
                self.provider.log.error("Provider WiFi tethering stopped.")
                return False
            if not tethering_check_internet_connection(
                    self.log, self.provider, [self.clients[0]], 10, 5):
                return False
        finally:
            if not wifi_tethering_cleanup(self.log, self.provider, [self.clients[0]]):
                return False
        return True

    @test_tracker_info(uuid="12a6c910-fa96-4d9b-99a5-8391fea33732")
    @TelephonyBaseTest.tel_test_wrap
    def test_toggle_apm_during_active_wifi_tethering(self):
        """WiFi Tethering test: Toggle APM during active WiFi Tethering

        1. DUT in LTE mode, idle.
        2. DUT start 2.4G WiFi Tethering
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB
        5. DUT toggle APM on, verify WiFi tethering stopped, PhoneB lost WiFi connection.
        6. DUT toggle APM off, verify PhoneA have cellular data and Internet connection.

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_4G):
            self.log.error("Verify 4G Internet access failed.")
            return False
        try:
            ssid = rand_ascii_str(10)
            if not wifi_tethering_setup_teardown(
                    self.log,
                    self.provider, [self.clients[0]],
                    ap_band=WIFI_CONFIG_APBAND_2G,
                    check_interval=10,
                    check_iteration=2,
                    do_cleanup=False,
                    ssid=ssid):
                self.log.error("WiFi Tethering failed.")
                return False

            if not verify_toggle_apm_tethering_internet_connection(self.log,
                                                                   self.provider,
                                                                   self.clients,
                                                                   ssid):
                return False
        finally:
            self.clients[0].droid.telephonyToggleDataConnection(True)
            wifi_reset(self.log, self.clients[0])
        return True

    @test_tracker_info(uuid="037e80fc-6eab-4cd1-846a-b9780a1d502d")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_entitlement_check(self):
        """Tethering Entitlement Check Test

        Get tethering entitlement check result.

        Returns:
            True if entitlement check returns True.
        """
        self.number_of_devices = 1

        return verify_tethering_entitlement_check(self.log,
                                                  self.provider)

    @test_tracker_info(uuid="4972826e-39ea-42f7-aae0-06fe3aa9ecc6")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_4g_to_2gwifi_stress(self):
        """Stress Test LTE to WiFI 2.4G Tethering

        This is a stress test for "test_tethering_4g_to_2gwifi".
        Default MINIMUM_SUCCESS_RATE is set to 95%.

        Returns:
            True stress pass rate is higher than MINIMUM_SUCCESS_RATE.
            False otherwise.
        """
        def precondition():
            return ensure_phones_default_state(self.log, self.android_devices)

        def test_case():
            return test_wifi_tethering(self.log,
                                       self.provider,
                                       self.clients,
                                       self.clients,
                                       RAT_4G,
                                       WIFI_CONFIG_APBAND_2G,
                                       check_interval=10,
                                       check_iteration=10)
        return run_stress_test(self.log, self.stress_test_number, precondition, test_case)

    @test_tracker_info(uuid="54e85aed-09e3-42e2-bb33-bca1005d93ab")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_wifi_ssid_quotes(self):
        """WiFi Tethering test: SSID name have quotes.
        1. Set SSID name have double quotes.
        2. Start LTE to WiFi (2.4G) tethering.
        3. Verify tethering.

        Returns:
            True if success.
            False if failed.
        """
        ssid = "\"" + rand_ascii_str(10) + "\""
        self.log.info(
            "Starting WiFi Tethering test with ssid: {}".format(ssid))

        return test_wifi_tethering(self.log,
                                   self.provider,
                                   self.clients,
                                   self.clients,
                                   None,
                                   WIFI_CONFIG_APBAND_2G,
                                   check_interval=10,
                                   check_iteration=10,
                                   ssid=ssid)

    @test_tracker_info(uuid="320326da-bf32-444d-81f9-f781c55dbc99")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_wifi_password_escaping_characters(self):
        """WiFi Tethering test: password have escaping characters.
        1. Set password have escaping characters.
            e.g.: '"DQ=/{Yqq;M=(^_3HzRvhOiL8S%`]w&l<Qp8qH)bs<4E9v_q=HLr^)}w$blA0Kg'
        2. Start LTE to WiFi (2.4G) tethering.
        3. Verify tethering.

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, None):
            self.log.error("Verify Internet access failed.")
            return False

        password = TETHERING_PASSWORD_HAS_ESCAPE
        self.log.info(
            "Starting WiFi Tethering test with password: {}".format(password))

        return wifi_tethering_setup_teardown(
            self.log,
            self.provider,
            self.clients,
            ap_band=WIFI_CONFIG_APBAND_2G,
            check_interval=10,
            check_iteration=10,
            password=password)

    @test_tracker_info(uuid="617c7e71-f166-465f-bfd3-b5a3a40cc0d4")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_wifi_ssid(self):
        """WiFi Tethering test: start WiFi tethering with all kinds of SSIDs.

        For each listed SSID, start WiFi tethering on DUT, client connect WiFi,
        then tear down WiFi tethering.

        Returns:
            True if WiFi tethering succeed on all SSIDs.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_4G):
            self.log.error("Setup Failed.")
            return False
        ssid_list = TETHERING_SPECIAL_SSID_LIST
        fail_list = {}

        for ssid in ssid_list:
            password = rand_ascii_str(8)
            self.log.info("SSID: <{}>, Password: <{}>".format(ssid, password))
            if not test_start_wifi_tethering_connect_teardown(self.log,
                                                          self.provider,
                                                          self.clients[0],
                                                          ssid,
                                                          password):
                fail_list[ssid] = password

        if len(fail_list) > 0:
            self.log.error("Failed cases: {}".format(fail_list))
            return False
        else:
            return True

    @test_tracker_info(uuid="9a5b5a34-b5cf-451d-94c4-8a64d456dfe5")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_wifi_password(self):
        """WiFi Tethering test: start WiFi tethering with all kinds of passwords.

        For each listed password, start WiFi tethering on DUT, client connect WiFi,
        then tear down WiFi tethering.

        Returns:
            True if WiFi tethering succeed on all passwords.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, RAT_4G):
            self.log.error("Setup Failed.")
            return False
        password_list = TETHERING_SPECIAL_PASSWORD_LIST
        fail_list = {}

        for password in password_list:
            ssid = rand_ascii_str(8)
            self.log.info("SSID: <{}>, Password: <{}>".format(ssid, password))
            if not test_start_wifi_tethering_connect_teardown(self.log,
                                                          self.provider,
                                                          self.clients[0],
                                                          ssid,
                                                          password):
                fail_list[ssid] = password

        if len(fail_list) > 0:
            self.log.error("Failed cases: {}".format(fail_list))
            return False
        else:
            return True

    @test_tracker_info(uuid="216bdb8c-edbf-4ff8-8750-a0861ab44df6")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_wifi_volte_call(self):
        """WiFi Tethering test: VoLTE call during WiFi tethering
        1. Start LTE to WiFi (2.4G) tethering.
        2. Verify tethering.
        3. Make outgoing VoLTE call on tethering provider.
        4. Verify tethering still works.
        5. Make incoming VoLTE call on tethering provider.
        6. Verify tethering still works.

        Returns:
            True if success.
            False if failed.
        """
        return test_tethering_wifi_and_voice_call(self.log, self.provider, self.clients,
            RAT_4G, phone_setup_volte, is_phone_in_call_volte)

    @test_tracker_info(uuid="bcd430cc-6d33-47d1-825d-aae9f248addc")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_wifi_csfb_call(self):
        """WiFi Tethering test: CSFB call during WiFi tethering
        1. Start LTE to WiFi (2.4G) tethering.
        2. Verify tethering.
        3. Make outgoing CSFB call on tethering provider.
        4. Verify tethering still works.
        5. Make incoming CSFB call on tethering provider.
        6. Verify tethering still works.

        Returns:
            True if success.
            False if failed.
        """
        return test_tethering_wifi_and_voice_call(self.log, self.provider, self.clients,
            RAT_4G, phone_setup_csfb, is_phone_in_call_csfb)

    @test_tracker_info(uuid="19e0df23-6819-4c69-bfda-eea9cce802d8")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_wifi_3g_call(self):
        """WiFi Tethering test: 3G call during WiFi tethering
        1. Start 3G to WiFi (2.4G) tethering.
        2. Verify tethering.
        3. Make outgoing CS call on tethering provider.
        4. Verify tethering still works.
        5. Make incoming CS call on tethering provider.
        6. Verify tethering still works.

        Returns:
            True if success.
            False if failed.
        """
        return test_tethering_wifi_and_voice_call(self.log, self.provider, self.clients,
            RAT_3G, phone_setup_voice_3g, is_phone_in_call_3g)

    @test_tracker_info(uuid="4acd98b5-fdef-4736-969f-3fa953990a58")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_wifi_no_password(self):
        """WiFi Tethering test: Start WiFi tethering with no password

        1. DUT is idle.
        2. DUT start 2.4G WiFi Tethering, with no WiFi password.
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, None):
            self.log.error("Verify Internet access failed.")
            return False

        return wifi_tethering_setup_teardown(
            self.log,
            self.provider, [self.clients[0]],
            ap_band=WIFI_CONFIG_APBAND_2G,
            check_interval=10,
            check_iteration=10,
            password="")

    @test_tracker_info(uuid="86ad1680-bfb8-457e-8b4d-23321cb3f223")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_wifi_reboot(self):
        """WiFi Tethering test: Start WiFi tethering then Reboot device

        1. DUT is idle.
        2. DUT start 2.4G WiFi Tethering.
        3. PhoneB disable data, connect to DUT's softAP
        4. Verify Internet access on DUT and PhoneB
        5. Reboot DUT
        6. After DUT reboot, verify tethering is stopped.

        Returns:
            True if success.
            False if failed.
        """
        try:
            if not test_wifi_tethering(self.log,
                                       self.provider,
                                       self.clients,
                                       [self.clients[0]],
                                       None,
                                       WIFI_CONFIG_APBAND_2G,
                                       check_interval=10,
                                       check_iteration=2,
                                       do_cleanup=False):
                return False

            if not verify_wifi_tethering_when_reboot(self.log,
                                                     self.provider):
                return False

        finally:
            if not wifi_tethering_cleanup(self.log, self.provider,
                                          self.clients):
                return False

        return True

    @test_tracker_info(uuid="5cf04ca2-dfde-43d6-be74-78b9abdf6c26")
    @TelephonyBaseTest.tel_test_wrap
    def test_connect_wifi_start_tethering_wifi_reboot(self):
        """WiFi Tethering test: WiFI connected, then start WiFi tethering,
            then reboot device.

        Initial Condition: DUT in 4G mode, idle, DUT connect to WiFi.
        1. DUT start 2.4G WiFi Tethering.
        2. PhoneB disable data, connect to DUT's softAP
        3. Verify Internet access on DUT and PhoneB
        4. Reboot DUT
        5. After DUT reboot, verify tethering is stopped. DUT is able to connect
            to previous WiFi AP.

        Returns:
            True if success.
            False if failed.
        """

        # Ensure provider connecting to wifi network.
        def setup_provider_internet_connection():
            return setup_device_internet_connection(self.log,
                                                    self.provider,
                                                    self.wifi_network_ssid,
                                                    self.wifi_network_pass)

        # wait for provider connecting to wifi network and verify
        # internet connection is working.
        def wait_and_verify_internet_connection():
            return wait_and_verify_device_internet_connection(self.log,
                                                              self.provider)

        try:
            if not test_wifi_tethering(self.log,
                                       self.provider,
                                       self.clients,
                                       [self.clients[0]],
                                       None,
                                       WIFI_CONFIG_APBAND_2G,
                                       check_interval=10,
                                       check_iteration=2,
                                       do_cleanup=False,
                                       pre_teardown_func=setup_provider_internet_connection):
                return False

            if not verify_wifi_tethering_when_reboot(self.log,
                                                     self.provider,
                                                     post_reboot_func=wait_and_verify_internet_connection):
                return False

        finally:
            if not wifi_tethering_cleanup(self.log,
                                          self.provider,
                                          self.clients):
                return False
        return True

    @test_tracker_info(uuid="e0621997-c5bd-4137-afa6-b43406e9c713")
    @TelephonyBaseTest.tel_test_wrap
    def test_connect_wifi_reboot_start_tethering_wifi(self):
        """WiFi Tethering test: DUT connected to WiFi, then reboot,
        After reboot, start WiFi tethering, verify tethering actually works.

        Initial Condition: Device set to 4G mode, idle, DUT connect to WiFi.
        1. Verify Internet is working on DUT (by WiFi).
        2. Reboot DUT.
        3. DUT start 2.4G WiFi Tethering.
        4. PhoneB disable data, connect to DUT's softAP
        5. Verify Internet access on DUT and PhoneB

        Returns:
            True if success.
            False if failed.
        """

        # Ensure provider connecting to wifi network and then reboot.
        def setup_provider_internet_connect_then_reboot():
            return setup_device_internet_connection_then_reboot(self.log,
                                                                self.provider,
                                                                self.wifi_network_ssid,
                                                                self.wifi_network_pass)
        return test_wifi_tethering(self.log,
                                   self.provider,
                                   self.clients,
                                   [self.clients[0]],
                                   None,
                                   WIFI_CONFIG_APBAND_2G,
                                   check_interval=10,
                                   check_iteration=2,
                                   pre_teardown_func=setup_provider_internet_connect_then_reboot)

    @test_tracker_info(uuid="89a849ef-e2ed-4bf2-ac31-81d34aba672a")
    @TelephonyBaseTest.tel_test_wrap
    def test_tethering_wifi_screen_off_enable_doze_mode(self):
        """WiFi Tethering test: Start WiFi tethering, then turn off DUT's screen,
            then enable doze mode, verify internet connection.

        1. Start WiFi tethering on DUT.
        2. PhoneB disable data, and connect to DUT's softAP
        3. Verify Internet access on DUT and PhoneB
        4. Turn off DUT's screen. Wait for 1 minute and
            verify Internet access on Client PhoneB.
        5. Enable doze mode on DUT. Wait for 1 minute and
            verify Internet access on Client PhoneB.
        6. Disable doze mode and turn off wifi tethering on DUT.

        Returns:
            True if success.
            False if failed.
        """
        try:
            if not test_wifi_tethering(self.log,
                                       self.provider,
                                       self.clients,
                                       [self.clients[0]],
                                       None,
                                       WIFI_CONFIG_APBAND_2G,
                                       check_interval=10,
                                       check_iteration=2,
                                       do_cleanup=False):
                return False
            if not verify_internet_connection_in_doze_mode(self.log,
                                                           self.provider,
                                                           self.clients[0]):
                return False

        finally:
            if not wifi_tethering_cleanup(self.log,
                                          self.provider,
                                          [self.clients[0]]):
                return False
        return True

    @test_tracker_info(uuid="695eef18-f759-4b41-8ad3-1fb329ee4b1b")
    @TelephonyBaseTest.tel_test_wrap
    def test_msim_switch_data_sim_2g(self):
        """Switch Data SIM on 2G network.

        Steps:
        1. Data on default Data SIM.
        2. Switch Data to another SIM. Make sure data is still available.
        3. Switch Data back to previous SIM. Make sure data is still available.

        Expected Results:
        1. Verify Data on Cell
        2. Verify Data on Wifi

        Returns:
            True if success.
            False if failed.
        """
        ad = self.android_devices[0]
        self.number_of_devices = 1
        current_data_sub_id = ad.droid.subscriptionGetDefaultDataSubId()
        current_sim_slot_index = get_slot_index_from_subid(
            ad, current_data_sub_id)
        if current_sim_slot_index == SIM1_SLOT_INDEX:
            next_sim_slot_index = SIM2_SLOT_INDEX
        else:
            next_sim_slot_index = SIM1_SLOT_INDEX
        next_data_sub_id = get_subid_from_slot_index(self.log, ad,
                                                     next_sim_slot_index)
        self.log.info("Current Data is on subId: {}, SIM slot: {}".format(
            current_data_sub_id, current_sim_slot_index))
        if not ensure_network_generation_for_subscription(
                self.log,
                ad,
                ad.droid.subscriptionGetDefaultDataSubId(),
                GEN_2G,
                voice_or_data=NETWORK_SERVICE_DATA):
            self.log.error("Device data does not attach to 2G.")
            return False
        if not verify_internet_connection(self.log, ad):
            self.log.error("No Internet access on default Data SIM.")
            return False

        self.log.info("Change Data to subId: {}, SIM slot: {}".format(
            next_data_sub_id, next_sim_slot_index))
        if not change_data_sim_and_verify_data(self.log, ad,
                                               next_sim_slot_index):
            self.log.error("Failed to change data SIM.")
            return False

        next_data_sub_id = current_data_sub_id
        next_sim_slot_index = current_sim_slot_index
        self.log.info("Change Data back to subId: {}, SIM slot: {}".format(
            next_data_sub_id, next_sim_slot_index))
        if not change_data_sim_and_verify_data(self.log, ad,
                                               next_sim_slot_index):
            self.log.error("Failed to change data SIM.")
            return False

        return True


    @test_tracker_info(uuid="9b8e92da-0ae1-472c-a72a-f6427e5405ce")
    @TelephonyBaseTest.tel_test_wrap
    def test_wifi_connect_disconnect_4g(self):
        """Perform multiple connects and disconnects from WiFi and verify that
            data switches between WiFi and Cell.

        Steps:
        1. DUT Cellular Data is on 4G. Reset Wifi on DUT
        2. Connect DUT to a WiFi AP
        3. Repeat steps 1-2, alternately disconnecting and disabling wifi

        Expected Results:
        1. Verify Data on Cell
        2. Verify Data on Wifi

        Returns:
            True if success.
            False if failed.
        """

        ad = self.android_devices[0]
        self.number_of_devices = 1

        if not ensure_network_generation_for_subscription(
                self.log, ad, ad.droid.subscriptionGetDefaultDataSubId(),
                GEN_4G, MAX_WAIT_TIME_NW_SELECTION, NETWORK_SERVICE_DATA):
            self.log.error("Device {} failed to reselect in {}s.".format(
                ad.serial, MAX_WAIT_TIME_NW_SELECTION))
            return False
        return test_wifi_connect_disconnect(self.log, ad, self.wifi_network_ssid, self.wifi_network_pass)

    @test_tracker_info(uuid="09893b1f-a4a2-49d3-8027-c2c91cb8742e")
    @TelephonyBaseTest.tel_test_wrap
    def test_wifi_connect_disconnect_3g(self):
        """Perform multiple connects and disconnects from WiFi and verify that
            data switches between WiFi and Cell.

        Steps:
        1. DUT Cellular Data is on 3G. Reset Wifi on DUT
        2. Connect DUT to a WiFi AP
        3. Repeat steps 1-2, alternately disconnecting and disabling wifi

        Expected Results:
        1. Verify Data on Cell
        2. Verify Data on Wifi

        Returns:
            True if success.
            False if failed.
        """

        ad = self.android_devices[0]
        self.number_of_devices = 1

        if not ensure_network_generation_for_subscription(
                self.log, ad, ad.droid.subscriptionGetDefaultDataSubId(),
                GEN_3G, MAX_WAIT_TIME_NW_SELECTION, NETWORK_SERVICE_DATA):
            self.log.error("Device {} failed to reselect in {}s.".format(
                ad.serial, MAX_WAIT_TIME_NW_SELECTION))
            return False
        return test_wifi_connect_disconnect(self.log, ad, self.wifi_network_ssid, self.wifi_network_pass)

    @test_tracker_info(uuid="0f095ca4-ce05-458f-9670-49a69f8c8270")
    @TelephonyBaseTest.tel_test_wrap
    def test_wifi_connect_disconnect_2g(self):
        """Perform multiple connects and disconnects from WiFi and verify that
            data switches between WiFi and Cell.

        Steps:
        1. DUT Cellular Data is on 2G. Reset Wifi on DUT
        2. Connect DUT to a WiFi AP
        3. Repeat steps 1-2, alternately disconnecting and disabling wifi

        Expected Results:
        1. Verify Data on Cell
        2. Verify Data on Wifi

        Returns:
            True if success.
            False if failed.
        """
        ad = self.android_devices[0]
        self.number_of_devices = 1

        if not ensure_network_generation_for_subscription(
                self.log, ad, ad.droid.subscriptionGetDefaultDataSubId(),
                GEN_2G, MAX_WAIT_TIME_NW_SELECTION, NETWORK_SERVICE_DATA):
            self.log.error("Device {} failed to reselect in {}s.".format(
                ad.serial, MAX_WAIT_TIME_NW_SELECTION))
            return False
        return test_wifi_connect_disconnect(self.log, ad, self.wifi_network_ssid, self.wifi_network_pass)

    def _test_wifi_tethering_enabled_add_voice_call(
            self, network_generation, voice_call_direction,
            is_data_available_during_call):
        """Tethering enabled + voice call.

        Steps:
        1. DUT data is on <network_generation>. Start WiFi Tethering.
        2. PhoneB connect to DUT's softAP
        3. DUT make a MO/MT (<voice_call_direction>) phone call.
        4. DUT end phone call.

        Expected Results:
        1. DUT is able to start WiFi tethering.
        2. PhoneB connected to DUT's softAP and able to browse Internet.
        3. DUT WiFi tethering is still on. Phone call works OK.
            If is_data_available_during_call is True, then PhoneB still has
            Internet access.
            Else, then Data is suspend, PhoneB has no Internet access.
        4. WiFi Tethering still on, voice call stopped, and PhoneB have Internet
            access.

        Returns:
            True if success.
            False if failed.
        """
        if not test_setup_tethering(self.log, self.provider, self.clients, network_generation):
            self.log.error("Verify Internet access failed.")
            return False
        try:
            # Start WiFi Tethering
            if not wifi_tethering_setup_teardown(
                    self.log,
                    self.provider, [self.clients[0]],
                    ap_band=WIFI_CONFIG_APBAND_2G,
                    check_interval=10,
                    check_iteration=2,
                    do_cleanup=False):
                self.log.error("WiFi Tethering failed.")
                return False

            if not self.provider.droid.wifiIsApEnabled():
                self.log.error("Provider WiFi tethering stopped.")
                return False

            # Make a voice call
            if voice_call_direction == DIRECTION_MOBILE_ORIGINATED:
                ad_caller = self.provider
                ad_callee = self.clients[0]
            else:
                ad_caller = self.clients[0]
                ad_callee = self.provider
            if not call_setup_teardown(self.log, ad_caller, ad_callee, None,
                                       None, None):
                self.log.error("Failed to Establish {} Voice Call".format(
                    voice_call_direction))
                return False

            # Tethering should still be on.
            if not self.provider.droid.wifiIsApEnabled():
                self.provider.log.error("Provider WiFi tethering stopped.")
                return False
            if not is_data_available_during_call:
                if verify_internet_connection(
                        self.log, self.clients[0], retry=0):
                    self.clients[0].log.error(
                        "Client should not have Internet Access.")
                    return False
            else:
                if not verify_internet_connection(self.log, self.clients[0]):
                    self.clients[0].error(
                        "Client should have Internet Access.")
                    return False

            # Hangup call. Client should have data.
            if not hangup_call(self.log, self.provider):
                self.provider.log.error("Failed to hang up call")
                return False
            if not self.provider.droid.wifiIsApEnabled():
                self.provider.log.error("Provider WiFi tethering stopped.")
                return False
            if not verify_internet_connection(self.log, self.clients[0]):
                self.clients[0].log.error(
                    "Client should have Internet Access.")
                return False
        finally:
            self.clients[0].droid.telephonyToggleDataConnection(True)
            wifi_reset(self.log, self.clients[0])
            if self.provider.droid.wifiIsApEnabled():
                stop_wifi_tethering(self.log, self.provider)
        return True

    @test_tracker_info(uuid="4d7a68c6-5eae-4242-a6e6-668f830caec3")
    @TelephonyBaseTest.tel_test_wrap
    def test_wifi_tethering_enabled_add_mo_voice_call_2g_dsds(self):
        """Tethering enabled + voice call

        Steps:
        1. DUT is DSDS device, Data on 2G. Start WiFi Tethering on <Data SIM>
        2. PhoneB connect to DUT's softAP
        3. DUT make a mo phone call on <Voice SIM>
        4. DUT end phone call.

        Expected Results:
        1. DUT is able to start WiFi tethering.
        2. PhoneB connected to DUT's softAP and able to browse Internet.
        3. DUT WiFi tethering is still on. Phone call works OK. Data is suspend,
            PhoneB still connected to DUT's softAP, but no data available.
        4. DUT data resumes, and PhoneB have Internet access.

        Returns:
            True if success.
            False if failed.
        """

        return self._test_wifi_tethering_enabled_add_voice_call(
            GEN_2G, DIRECTION_MOBILE_ORIGINATED, False)

    @test_tracker_info(uuid="de720069-a46c-4a6f-ae80-60b9349c8528")
    @TelephonyBaseTest.tel_test_wrap
    def test_wifi_tethering_enabled_add_mt_voice_call_2g_dsds(self):
        """Tethering enabled + voice call

        Steps:
        1. DUT is DSDS device, Data on 2G. Start WiFi Tethering on <Data SIM>
        2. PhoneB connect to DUT's softAP
        3. DUT make a mt phone call on <Voice SIM>
        4. DUT end phone call.

        Expected Results:
        1. DUT is able to start WiFi tethering.
        2. PhoneB connected to DUT's softAP and able to browse Internet.
        3. DUT WiFi tethering is still on. Phone call works OK. Data is suspend,
            PhoneB still connected to DUT's softAP, but no data available.
        4. DUT data resumes, and PhoneB have Internet access.

        Returns:
            True if success.
            False if failed.
        """

        return self._test_wifi_tethering_enabled_add_voice_call(
            GEN_2G, DIRECTION_MOBILE_TERMINATED, False)

    @test_tracker_info(uuid="fad169c0-8ae6-45d2-98ba-3fb60466ff0b")
    @TelephonyBaseTest.tel_test_wrap
    def test_wifi_tethering_msim_switch_data_sim(self):
        """Tethering enabled + switch data SIM.

        Steps:
        1. Start WiFi Tethering on <Default Data SIM>
        2. PhoneB connect to DUT's softAP
        3. DUT change Default Data SIM.

        Expected Results:
        1. DUT is able to start WiFi tethering.
        2. PhoneB connected to DUT's softAP and able to browse Internet.
        3. DUT Data changed to 2nd SIM, WiFi tethering should continues,
            PhoneB should have Internet access.

        Returns:
            True if success.
            False if failed.
        """
        current_data_sub_id = self.provider.droid.subscriptionGetDefaultDataSubId(
        )
        current_sim_slot_index = get_slot_index_from_subid(
            self.provider, current_data_sub_id)
        self.provider.log.info("Current Data is on subId: %s, SIM slot: %s",
                               current_data_sub_id, current_sim_slot_index)
        if not test_setup_tethering(self.log, self.provider, self.clients, None):
            self.log.error("Verify Internet access failed.")
            return False
        try:
            # Start WiFi Tethering
            if not wifi_tethering_setup_teardown(
                    self.log,
                    self.provider, [self.clients[0]],
                    ap_band=WIFI_CONFIG_APBAND_2G,
                    check_interval=10,
                    check_iteration=2,
                    do_cleanup=False):
                self.log.error("WiFi Tethering failed.")
                return False
            for i in range(0, 2):
                next_sim_slot_index = \
                    {SIM1_SLOT_INDEX : SIM2_SLOT_INDEX,
                     SIM2_SLOT_INDEX : SIM1_SLOT_INDEX}[current_sim_slot_index]
                self.log.info(
                    "Change Data to SIM slot: {}".format(next_sim_slot_index))
                if not change_data_sim_and_verify_data(self.log, self.provider,
                                                       next_sim_slot_index):
                    self.provider.log.error("Failed to change data SIM.")
                    return False
                current_sim_slot_index = next_sim_slot_index
                if not verify_internet_connection(self.log, self.clients[0]):
                    self.clients[0].log.error(
                        "Client should have Internet Access.")
                    return False
        finally:
            self.clients[0].droid.telephonyToggleDataConnection(True)
            wifi_reset(self.log, self.clients[0])
            if self.provider.droid.wifiIsApEnabled():
                stop_wifi_tethering(self.log, self.provider)
        return True

    @test_tracker_info(uuid="8bb9383f-ddf9-400c-a831-c9462bae6b47")
    @TelephonyBaseTest.tel_test_wrap
    def test_msim_cell_data_switch_to_wifi_switch_data_sim_2g(self):
        """Switch Data SIM on 2G network.

        Steps:
        1. Data on default Data SIM.
        2. Turn on WiFi, then data should be on WiFi.
        3. Switch Data to another SIM. Disable WiFi.

        Expected Results:
        1. Verify Data on Cell
        2. Verify Data on WiFi
        3. After WiFi disabled, Cell Data is available on 2nd SIM.

        Returns:
            True if success.
            False if failed.
        """
        ad = self.android_devices[0]
        self.number_of_devices = 1

        current_data_sub_id = ad.droid.subscriptionGetDefaultDataSubId()
        current_sim_slot_index = get_slot_index_from_subid(
            ad, current_data_sub_id)
        if current_sim_slot_index == SIM1_SLOT_INDEX:
            next_sim_slot_index = SIM2_SLOT_INDEX
        else:
            next_sim_slot_index = SIM1_SLOT_INDEX
        next_data_sub_id = get_subid_from_slot_index(self.log, ad,
                                                     next_sim_slot_index)
        self.log.info("Current Data is on subId: {}, SIM slot: {}".format(
            current_data_sub_id, current_sim_slot_index))
        if not ensure_network_generation_for_subscription(
                self.log,
                ad,
                ad.droid.subscriptionGetDefaultDataSubId(),
                GEN_2G,
                voice_or_data=NETWORK_SERVICE_DATA):
            self.log.error("Device data does not attach to 2G.")
            return False
        if not verify_internet_connection(self.log, ad):
            self.log.error("No Internet access on default Data SIM.")
            return False

        self.log.info("Connect to WiFi and verify Internet access.")
        if not ensure_wifi_connected(self.log, ad, self.wifi_network_ssid,
                                     self.wifi_network_pass):
            self.log.error("WiFi connect fail.")
            return False
        if (not wait_for_wifi_data_connection(self.log, ad, True)
                or not verify_internet_connection(self.log, ad)):
            self.log.error("Data is not on WiFi")
            return False

        try:
            self.log.info(
                "Change Data SIM, Disable WiFi and verify Internet access.")
            set_subid_for_data(ad, next_data_sub_id)
            wifi_toggle_state(self.log, ad, False)
            if not wait_for_data_attach_for_subscription(
                    self.log, ad, next_data_sub_id,
                    MAX_WAIT_TIME_NW_SELECTION):
                self.log.error("Failed to attach data on subId:{}".format(
                    next_data_sub_id))
                return False
            if not verify_internet_connection(self.log, ad):
                self.log.error("No Internet access after changing Data SIM.")
                return False

        finally:
            self.log.info("Change Data SIM back.")
            set_subid_for_data(ad, current_data_sub_id)

        return True

    @test_tracker_info(uuid="ef03eff7-ddd3-48e9-8f67-5e271e14048b")
    @TelephonyBaseTest.tel_test_wrap
    def test_vzw_embms_services(self):
        ad = self.android_devices[0]
        self.number_of_devices = 1

        # Install App and Push config
        self.log.info("Pushing embms config and apk to the Android device.")
        android_embms_path = "/sdcard/mobitv"
        embms_path = self.user_params.get("embms_path", "embms_path")
        if isinstance(embms_path, list):
            embms_path = embms_path[0]
        ad.adb.shell("mkdir /sdcard/mobitv")
        dcafile = os.path.join(embms_path, "dca.config")
        apkfile = os.path.join(embms_path, "VzwDCA.apk")
        ad.adb.push("%s %s" % (dcafile, android_embms_path))
        ad.adb.install("%s" % apkfile)

        # Co-ordinates Mapping
        lcd_density = ad.adb.shell("getprop ro.sf.lcd_density")
        ad.log.debug("lcd_density %s" % lcd_density)
        if lcd_density in ["420", "440"]:
            agree_y_axis = 1000
        else:
            agree_y_axis = 1300

        # Screen ON needed to open the VZW App
        if "ON" in \
        ad.adb.shell(
               "dumpsys power | grep 'Display Power: state' | cut -d '=' -f2"):
            ad.log.info("Screen already ON")
            ad.adb.shell("input keyevent 82")
        else:
            ad.log.info("Screen OFF, turning ON")
            ad.adb.shell("input keyevent 26")
            ad.adb.shell("input keyevent 82")

        try:
            # Check if app is installed
            if ad.is_apk_installed("com.mobitv.vzwdca"):
                ad.log.info("VZWDCA App is successfully installed")
            else:
                ad.log.error("VZWDCA App is not installed")
                return False

            # Grant Permissions, Start, Agree, Register
            for cmd in ("pm grant com.mobitv.vzwdca "
                        "android.permission.READ_EXTERNAL_STORAGE",
                        "pm grant com.mobitv.vzwdca "
                        "android.permission.WRITE_EXTERNAL_STORAGE",
                        "am start -a android.intent.action.VIEW -n "
                        "com.mobitv.vzwdca/.DcaActivity",
                        "input tap 500 %d" % agree_y_axis, "input keyevent 61",
                        "input keyevent 61", "input keyevent 61",
                        "input keyevent 61", "input keyevent 61",
                        "input keyevent 66"):
                time.sleep(1)
                ad.log.info(cmd)
                ad.adb.shell(cmd)

            # Check Reg-DeReg
            time.sleep(5)
            if ad.is_apk_running("com.qualcomm.ltebc_vzw"):
                ad.log.info("EMBMS Registered successfully")
                ad.adb.shell("input keyevent 61")
                time.sleep(1)
                ad.adb.shell("input keyevent 66")
                time.sleep(1)
                if not ad.is_apk_running("com.qualcomm.ltebc_vzw"):
                    ad.log.info("EMBMS De-Registered successfully")
                    return True
                else:
                    ad.log.error("EMBMS De-Registeration Failed")
                    return False
            else:
                ad.log.error("EMBMS Registeration Failed")
                return False
        finally:
            ad.log.info("Force Close the VZW App")
            ad.adb.shell("am force-stop com.mobitv.vzwdca")

    @test_tracker_info(uuid="8a8cd773-77f5-4802-85ac-1a654bb4743c")
    @TelephonyBaseTest.tel_test_wrap
    def test_disable_data_on_non_active_data_sim(self):
        """Switch Data SIM on 2G network.

        Steps:
        1. Data on default Data SIM.
        2. Disable data on non-active Data SIM.

        Expected Results:
        1. Verify Data Status on Default Data SIM and non-active Data SIM.
        1. Verify Data Status on Default Data SIM and non-active Data SIM.

        Returns:
            True if success.
            False if failed.
        """
        ad = self.android_devices[0]
        self.number_of_devices = 1
        current_data_sub_id = ad.droid.subscriptionGetDefaultDataSubId()
        current_sim_slot_index = get_slot_index_from_subid(
            ad, current_data_sub_id)
        if current_sim_slot_index == SIM1_SLOT_INDEX:
            non_active_sim_slot_index = SIM2_SLOT_INDEX
        else:
            non_active_sim_slot_index = SIM1_SLOT_INDEX
        non_active_sub_id = get_subid_from_slot_index(
            self.log, ad, non_active_sim_slot_index)
        self.log.info("Current Data is on subId: {}, SIM slot: {}".format(
            current_data_sub_id, current_sim_slot_index))

        if not ensure_network_generation_for_subscription(
                self.log,
                ad,
                ad.droid.subscriptionGetDefaultDataSubId(),
                GEN_2G,
                voice_or_data=NETWORK_SERVICE_DATA):
            self.log.error("Device data does not attach to 2G.")
            return False
        if not verify_internet_connection(self.log, ad):
            self.log.error("No Internet access on default Data SIM.")
            return False

        if ad.droid.telephonyGetDataConnectionState() != DATA_STATE_CONNECTED:
            self.log.error("Data Connection State should be connected.")
            return False
        # TODO: Check Data state for non-active subId.

        try:
            self.log.info("Disable Data on Non-Active Sub ID")
            ad.droid.telephonyToggleDataConnectionForSubscription(
                non_active_sub_id, False)
            # TODO: Check Data state for non-active subId.
            if ad.droid.telephonyGetDataConnectionState(
            ) != DATA_STATE_CONNECTED:
                self.log.error("Data Connection State should be connected.")
                return False
        finally:
            self.log.info("Enable Data on Non-Active Sub ID")
            ad.droid.telephonyToggleDataConnectionForSubscription(
                non_active_sub_id, True)
        return True

    def file_download_stress(self):
        failure = 0
        total_count = 0
        self.result_info = collections.defaultdict(int)
        dut = self.android_devices[0]
        self.number_of_devices = 1
        self.max_sleep_time = int(self.user_params.get("max_sleep_time", 1200))
        #file_names = ["5MB", "10MB", "20MB", "50MB", "200MB", "512MB", "1GB"]
        file_names = ["5MB", "10MB", "20MB", "50MB", "200MB", "512MB"]
        while total_count < self.stress_test_number:
            total_count += 1
            try:
                dut.log.info(dict(self.result_info))
                selection = random.randrange(0, len(file_names))
                file_name = file_names[selection]
                self.result_info["Total %s file download" % file_name] += 1
                if not active_file_download_test(self.log, dut, file_name):
                    self.result_info["%s file download failure" %
                                     file_name] += 1
                    failure += 1
                    dut.take_bug_report("%s_failure_%s" % (self.test_name,
                                                           failure),
                                        time.strftime("%m-%d-%Y-%H-%M-%S"))
                    self.dut.droid.goToSleepNow()
                    time.sleep(random.randrange(0, self.max_sleep_time))
            except Exception as e:
                self.log.error("Exception error %s", str(e))
                self.result_info["Exception Errors"] += 1
            dut.log.info("File download test failure: %s/%s", failure,
                         total_count)
        if failure / total_count > 0.1:
            dut.log.error("File download test failure: %s/%s", failure,
                          total_count)
            return False
        return True

    @test_tracker_info(uuid="5381a6fa-6771-4b00-a0d6-4a3891a6dba8")
    @TelephonyBaseTest.tel_test_wrap
    def test_file_download_stress_default(self):
        """File download stress test

        Steps:
        1. Download a file random picked.
        2. Device sleep for sometime and Repeat 1.

        Expected Results:
        Total download failure rate is less than 10%.

        Returns:
            True if success.
            False if failed.
        """
        return self.file_download_stress()

    @test_tracker_info(uuid="c9970955-123b-467c-afbb-95ec8f99e9b7")
    def test_file_download_with_mobile_data_usage_limit_set(self):
        """ Steps:

        1. Set the data usage limit to current data usage + 9MB
        2. Download 5MB file from internet.
        3. The first file download should succeed
        4. The second file download should fail

        """
        dut = self.android_devices[0]
        self.number_of_devices = 1
        ensure_phones_default_state(self.log, [dut])
        subscriber_id = dut.droid.telephonyGetSubscriberId()
        old_data_usage = get_mobile_data_usage(dut, subscriber_id)

        # set data usage limit to current usage limit + 10MB
        data_limit = old_data_usage + 9 * 1000 * 1000
        set_mobile_data_usage_limit(dut, data_limit, subscriber_id)

        # download file - size 5MB twice
        try:
            for _ in range(2):
                if not active_file_download_test(self.log, dut, "5MB", "curl"):
                    if get_mobile_data_usage(
                            dut, subscriber_id) + 5 * 1000 * 1000 < data_limit:
                        dut.log.error(
                            "Fail to download file when mobile data usage is"
                            " below data usage limit")
                        return False
                    else:
                        dut.log.info(
                            "Download fails as expected due to data limit reached"
                        )
                else:
                    if get_mobile_data_usage(dut, subscriber_id) < data_limit:
                        dut.log.info(
                            "Download file succeed when mobile data usage is"
                            " below data usage limit")
                    else:
                        dut.log.error(
                            "Download should fail due to data limit reached")
                        return False
            return True
        finally:
            remove_mobile_data_usage_limit(dut, subscriber_id)


    def _test_data_stall_detection_recovery(self, nw_type="cellular",
                                            validation_type="detection"):
        dut = self.android_devices[0]
        self.number_of_devices = 1

        try:
            cmd = ('ss -l -p -n | grep "tcp.*droid_script" | tr -s " " '
                   '| cut -d " " -f 5 | sed s/.*://g')
            sl4a_port = dut.adb.shell(cmd)
            ensure_phones_default_state(self.log, [dut])
            if nw_type == "wifi":
                if not ensure_wifi_connected(self.log, dut,
                                self.wifi_network_ssid, self.wifi_network_pass):
                    return False

            if not test_data_browsing_success_using_sl4a(self.log, dut):
                dut.log.error("Browsing failed before the test, aborting!")
                return False

            begin_time = get_device_epoch_time(dut)
            break_internet_except_sl4a_port(dut, sl4a_port)

            if not test_data_browsing_failure_using_sl4a(self.log, dut):
                dut.log.error("Browsing success even after breaking internet, "\
                              "aborting!")
                return False

            if not check_data_stall_detection(dut):
                dut.log.error("NetworkMonitor unable to detect Data Stall")

            if not check_network_validation_fail(dut, begin_time):
                dut.log.error("Unable to detect NW validation fail")
                return False

            if validation_type == "recovery":
                if not check_data_stall_recovery(dut, begin_time):
                    dut.log.error("Recovery was not triggerred")
                    return False

            resume_internet_with_sl4a_port(dut, sl4a_port)
            time.sleep(10)

            if not test_data_browsing_success_using_sl4a(self.log, dut):
                dut.log.error("Browsing failed after resuming internet")
                return False
            return True
        finally:
            resume_internet_with_sl4a_port(dut, sl4a_port)


    def _test_airplane_mode_stress(self):
        ad = self.android_devices[0]
        self.number_of_devices = 1
        total_iteration = self.stress_test_number
        fail_count = collections.defaultdict(int)
        current_iteration = 1
        for i in range(1, total_iteration + 1):
            msg = "Airplane mode test Iteration: <%s> / <%s>" % (i, total_iteration)
            self.log.info(msg)
            if not airplane_mode_test(self.log, ad):
                fail_count["apm_run"] += 1
                ad.log.error(">----Iteration : %d/%d failed.----<",
                             i, total_iteration)
            ad.log.info(">----Iteration : %d/%d succeeded.----<",
                        i, total_iteration)
            current_iteration += 1
        test_result = True
        for failure, count in fail_count.items():
            if count:
                ad.log.error("%s: %s %s failures in %s iterations",
                             self.test_name, count, failure,
                             total_iteration)
                test_result = False
        return test_result


    @test_tracker_info(uuid="3a82728f-18b5-4a35-9eab-4e6cf55271d9")
    @TelephonyBaseTest.tel_test_wrap
    def test_apm_toggle_stress(self):
        """ Test airplane mode toggle

        1. Start with airplane mode off
        2. Toggle airplane mode on
        3. Toggle airplane mode off
        4. Repeat above steps

        Returns:
            True if pass; False if fail.
        """
        return self._test_airplane_mode_stress()


    @test_tracker_info(uuid="fda33416-698a-408f-8ddc-b5cde13b1f83")
    @TelephonyBaseTest.tel_test_wrap
    def test_data_stall_detection_cellular(self):
        """ Data Stall Detection Testing

        1. Ensure device is camped, browsing working fine
        2. Break Internet access, browsing should fail
        3. Check for Data Stall Detection

        """
        return self._test_data_stall_detection_recovery(nw_type="cellular")


    @test_tracker_info(uuid="a57891d6-7892-46c7-8bca-23cd2cca8552")
    @TelephonyBaseTest.tel_test_wrap
    def test_data_stall_detection_wifi(self):
        """ Data Stall Detection Testing

        1. Ensure device is connected to WiFi, browsing working fine
        2. Break Internet access, browsing should fail
        3. Check for Data Stall Detection

        """
        return self._test_data_stall_detection_recovery(nw_type="wifi")


    @test_tracker_info(uuid="16d3f123-cac3-45a9-a2e5-c01bab7044d4")
    @TelephonyBaseTest.tel_test_wrap
    def test_data_stall_recovery_cellular(self):
        """ Data Stall Recovery Testing

        1. Ensure device is camped, browsing working fine
        2. Break Internet access, browsing should fail
        3. Check for Data Stall Detection
        4. Check for Data Stall Recovery

        """
        return self._test_data_stall_detection_recovery(nw_type="cellular",
                                                validation_type="recovery")

    @test_tracker_info(uuid="d705d653-c810-42eb-bd07-3313f99be2fa")
    @TelephonyBaseTest.tel_test_wrap
    def test_browsing_4g(self):
        ad = self.android_devices[0]
        self.number_of_devices = 1

        self.log.info("Connect to LTE and verify internet connection.")
        if not phone_setup_4g(self.log, ad):
            return False
        if not verify_internet_connection(self.log, ad):
            return False

        return browsing_test(self.log, self.android_devices[0])

    @test_tracker_info(uuid="71088cb1-5ccb-4d3a-8e6a-03fac9bf31cc")
    @TelephonyBaseTest.tel_test_wrap
    def test_browsing_wifi(self):
        ad = self.android_devices[0]
        self.number_of_devices = 1

        self.log.info("Connect to Wi-Fi and verify internet connection.")
        if not ensure_wifi_connected(self.log, ad, self.wifi_network_ssid,
                                     self.wifi_network_pass):
            return False
        if not wait_for_wifi_data_connection(self.log, ad, True):
            return False
        if not verify_internet_connection(self.log, ad):
            return False

        return browsing_test(self.log, self.android_devices[0], wifi_ssid=self.wifi_network_ssid)

    def _test_sync_time_from_network(self, ad, data_on=True):
        """ Verifies time recovered by nitz service

        1. Toggle mobile data
        2. Toggle off network time synchronization
        3. Change device time to FAKE_DATE_TIME: Jan,2,2019 03:04:05
        4. Toggle on network time synchronization
        5. Verify the year is changed back.
        6. Recover mobile data

        Args:
            ad: android device object
            data_on: conditional mobile data on or off

        Returns:
            True if pass; False if fail.
        """
        if not(data_on):
            ad.log.info("Disable mobile data.")
            ad.droid.telephonyToggleDataConnection(False)
        set_time_sync_from_network(ad, "disable")
        ad.log.info("Set device time to Jan,2,2019 03:04:05")
        datetime_handle(ad, 'set', set_datetime_value = FAKE_DATE_TIME)
        datetime_before_sync = datetime_handle(ad, 'get')
        ad.log.info("Got before sync datetime from device: %s",
                        datetime_before_sync)
        device_year = datetime_handle(ad, 'get', get_year = True)

        if (device_year != FAKE_YEAR):
            raise signals.TestSkip("Set device time failed, skip test.")
        set_time_sync_from_network(ad, "enable")
        datetime_after_sync = datetime_handle(ad, "get")
        ad.log.info("Got after sync datetime from device: %s",
                        datetime_after_sync)
        device_year = datetime_handle(ad, "get", get_year = True)

        if not(data_on):
            ad.log.info("Enabling mobile data.")
            ad.droid.telephonyToggleDataConnection(True)

        if (device_year != FAKE_YEAR):
            self.record_data({
                "Test Name": "test_sync_time_from_network",
                "sponge_properties": {
                    "result": "pass",
                },
            })
            return True
        else:
            return False

    @test_tracker_info(uuid="1017b655-5d79-44d2-86ff-675c69aec26b")
    @TelephonyBaseTest.tel_test_wrap
    def test_sync_time_from_network(self):
        """ Test device time recovered by nitz service

        1. Toggle off network time synchronization
        2. Change device time to FAKE_DATE_TIME.
        3. Toggle on network time synchronization
        4. Verify the year is changed back.

        """
        ad = self.android_devices[0]
        self.number_of_devices = 1

        wifi_toggle_state(ad.log, ad, False)
        return self._test_sync_time_from_network(ad)

    @test_tracker_info(uuid="46d170c6-a632-4124-889b-96caa0e641da")
    @TelephonyBaseTest.tel_test_wrap
    def test_sync_time_from_network_data_off(self):
        """ Test device time recovered by nitz service

        1. Toggle off mobile data
        2. Toggle off network time synchronization
        3. Change device time to FAKE_DATE_TIME.
        4. Toggle on network time synchronization
        5. Verify the year is changed back.

        """
        ad = self.android_devices[0]
        self.number_of_devices = 1

        wifi_toggle_state(ad.log, ad, False)
        return self._test_sync_time_from_network(ad, data_on=False)

    @test_tracker_info(uuid="2d739779-3beb-4e6e-8396-84f28e626379")
    @TelephonyBaseTest.tel_test_wrap
    def test_reboot_4g(self):
        ad = self.android_devices[0]
        self.number_of_devices = 1

        self.log.info("Connect to LTE and verify internet connection.")
        if not phone_setup_4g(self.log, ad):
            return False
        if not verify_internet_connection(self.log, ad):
            return False

        return reboot_test(self.log, ad)

    @test_tracker_info(uuid="5ce671f7-c2a4-46aa-a9f2-e5571c144fad")
    @TelephonyBaseTest.tel_test_wrap
    def test_reboot_3g(self):
        ad = self.android_devices[0]
        self.number_of_devices = 1

        self.log.info("Connect to 3G and verify internet connection.")
        if not phone_setup_3g(self.log, ad):
            return False
        if not verify_internet_connection(self.log, ad):
            return False

        return reboot_test(self.log, ad)

    @test_tracker_info(uuid="9e094f0e-7bef-479e-a5fa-a6bfa95289a5")
    @TelephonyBaseTest.tel_test_wrap
    def test_reboot_wifi(self):
        ad = self.android_devices[0]
        self.number_of_devices = 1

        self.log.info("Connect to Wi-Fi and verify internet connection.")
        if not ensure_wifi_connected(self.log, ad, self.wifi_network_ssid,
                                     self.wifi_network_pass):
            return False
        if not wait_for_wifi_data_connection(self.log, ad, True):
            return False
        if not verify_internet_connection(self.log, ad):
            return False

        return reboot_test(self.log, ad, wifi_ssid=self.wifi_network_ssid)

    """ Tests End """
