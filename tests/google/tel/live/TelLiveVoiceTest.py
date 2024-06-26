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

import time

from acts import signals
from acts.test_decorators import test_tracker_info
from acts_contrib.test_utils.tel.loggers.protos.telephony_metric_pb2 import TelephonyVoiceTestResult
from acts_contrib.test_utils.tel.loggers.telephony_metric_logger import TelephonyMetricLogger
from acts_contrib.test_utils.tel.TelephonyBaseTest import TelephonyBaseTest
from acts_contrib.test_utils.tel.tel_data_utils import get_mobile_data_usage
from acts_contrib.test_utils.tel.tel_data_utils import remove_mobile_data_usage_limit
from acts_contrib.test_utils.tel.tel_data_utils import set_mobile_data_usage_limit
from acts_contrib.test_utils.tel.tel_data_utils import test_call_setup_in_active_data_transfer
from acts_contrib.test_utils.tel.tel_data_utils import test_call_setup_in_active_youtube_video
from acts_contrib.test_utils.tel.tel_data_utils import call_epdg_to_epdg_wfc
from acts_contrib.test_utils.tel.tel_data_utils import test_wifi_cell_switching_in_call
from acts_contrib.test_utils.tel.tel_defines import CARRIER_VZW
from acts_contrib.test_utils.tel.tel_defines import DIRECTION_MOBILE_ORIGINATED
from acts_contrib.test_utils.tel.tel_defines import DIRECTION_MOBILE_TERMINATED
from acts_contrib.test_utils.tel.tel_defines import GEN_2G
from acts_contrib.test_utils.tel.tel_defines import GEN_4G
from acts_contrib.test_utils.tel.tel_defines import GEN_3G
from acts_contrib.test_utils.tel.tel_defines import PHONE_TYPE_CDMA
from acts_contrib.test_utils.tel.tel_defines import PHONE_TYPE_GSM
from acts_contrib.test_utils.tel.tel_defines import TOTAL_LONG_CALL_DURATION
from acts_contrib.test_utils.tel.tel_defines import WAIT_TIME_IN_CALL
from acts_contrib.test_utils.tel.tel_defines import WAIT_TIME_IN_CALL_FOR_IMS
from acts_contrib.test_utils.tel.tel_defines import WAIT_TIME_ANDROID_STATE_SETTLING
from acts_contrib.test_utils.tel.tel_defines import WFC_MODE_CELLULAR_PREFERRED
from acts_contrib.test_utils.tel.tel_defines import WFC_MODE_WIFI_ONLY
from acts_contrib.test_utils.tel.tel_defines import WFC_MODE_WIFI_PREFERRED
from acts_contrib.test_utils.tel.tel_phone_setup_utils import phone_idle_2g
from acts_contrib.test_utils.tel.tel_phone_setup_utils import phone_idle_3g
from acts_contrib.test_utils.tel.tel_phone_setup_utils import phone_idle_csfb
from acts_contrib.test_utils.tel.tel_phone_setup_utils import phone_idle_iwlan
from acts_contrib.test_utils.tel.tel_phone_setup_utils import phone_idle_volte
from acts_contrib.test_utils.tel.tel_phone_setup_utils import phone_setup_csfb
from acts_contrib.test_utils.tel.tel_phone_setup_utils import phone_setup_iwlan
from acts_contrib.test_utils.tel.tel_phone_setup_utils import phone_setup_iwlan_cellular_preferred
from acts_contrib.test_utils.tel.tel_phone_setup_utils import phone_setup_voice_2g
from acts_contrib.test_utils.tel.tel_phone_setup_utils import phone_setup_voice_3g
from acts_contrib.test_utils.tel.tel_phone_setup_utils import phone_setup_voice_general
from acts_contrib.test_utils.tel.tel_phone_setup_utils import phone_setup_volte
from acts_contrib.test_utils.tel.tel_subscription_utils import get_incoming_voice_sub_id
from acts_contrib.test_utils.tel.tel_subscription_utils import get_outgoing_voice_sub_id
from acts_contrib.test_utils.tel.tel_test_utils import get_phone_number
from acts_contrib.test_utils.tel.tel_test_utils import install_dialer_apk
from acts_contrib.test_utils.tel.tel_test_utils import num_active_calls
from acts_contrib.test_utils.tel.tel_test_utils import STORY_LINE
from acts_contrib.test_utils.tel.tel_voice_utils import hangup_call
from acts_contrib.test_utils.tel.tel_voice_utils import hold_unhold_test
from acts_contrib.test_utils.tel.tel_voice_utils import initiate_call
from acts_contrib.test_utils.tel.tel_voice_utils import is_phone_in_call
from acts_contrib.test_utils.tel.tel_voice_utils import is_phone_in_call_1x
from acts_contrib.test_utils.tel.tel_voice_utils import is_phone_in_call_2g
from acts_contrib.test_utils.tel.tel_voice_utils import is_phone_in_call_3g
from acts_contrib.test_utils.tel.tel_voice_utils import is_phone_in_call_csfb
from acts_contrib.test_utils.tel.tel_voice_utils import is_phone_in_call_iwlan
from acts_contrib.test_utils.tel.tel_voice_utils import is_phone_in_call_not_iwlan
from acts_contrib.test_utils.tel.tel_voice_utils import is_phone_in_call_wcdma
from acts_contrib.test_utils.tel.tel_voice_utils import is_phone_in_call_volte
from acts_contrib.test_utils.tel.tel_voice_utils import _test_call_long_duration
from acts_contrib.test_utils.tel.tel_voice_utils import call_setup_teardown
from acts_contrib.test_utils.tel.tel_voice_utils import call_voicemail_erase_all_pending_voicemail
from acts_contrib.test_utils.tel.tel_voice_utils import two_phone_call_leave_voice_mail
from acts_contrib.test_utils.tel.tel_voice_utils import two_phone_call_long_seq
from acts_contrib.test_utils.tel.tel_voice_utils import two_phone_call_short_seq
from acts_contrib.test_utils.tel.tel_voice_utils import wait_and_answer_call
from acts_contrib.test_utils.tel.tel_voice_utils import wait_for_in_call_active
from acts_contrib.test_utils.tel.tel_voice_utils import wait_for_ringing_call
from acts_contrib.test_utils.tel.tel_wifi_utils import set_wifi_to_default
from acts_contrib.test_utils.tel.tel_wifi_utils import wifi_toggle_state
from acts.libs.utils.multithread import multithread_func

DEFAULT_PING_DURATION = 120  # in seconds

CallResult = TelephonyVoiceTestResult.CallResult.Value


class TelLiveVoiceTest(TelephonyBaseTest):
    def setup_class(self):
        super().setup_class()

        self.stress_test_number = self.get_stress_test_number()
        self.long_call_duration = self.user_params.get(
            "long_call_duration",
            TOTAL_LONG_CALL_DURATION)
        self.number_of_devices = 2
        self.call_server_number = self.user_params.get(
                "call_server_number", STORY_LINE)
        self.tel_logger = TelephonyMetricLogger.for_test_case()
        self.dialer_util = self.user_params.get("dialer_apk", None)
        if isinstance(self.dialer_util, list):
            self.dialer_util = self.dialer_util[0]

        if self.dialer_util:
            ads = self.android_devices
            for ad in ads:
                install_dialer_apk(ad, self.dialer_util)

    def get_carrier_name(self, ad):
        return ad.adb.getprop("gsm.sim.operator.alpha")

    def check_band_support(self,ad):
        carrier = ad.adb.getprop("gsm.sim.operator.alpha")

        if int(ad.adb.getprop("ro.product.first_api_level")) > 30 and (
                carrier == CARRIER_VZW):
            raise signals.TestSkip(
                "Device Doesn't Support 2g/3G Band.")

    def _is_phone_in_call_not_iwlan(self):
        return is_phone_in_call_not_iwlan(self.log, self.android_devices[0])

    def _is_phone_in_call_iwlan(self):
        return is_phone_in_call_iwlan(self.log, self.android_devices[0])


    """ Tests Begin """

    @TelephonyBaseTest.tel_test_wrap
    @test_tracker_info(uuid="c5009f8c-eb1d-4cd9-85ce-604298bbeb3e")
    def test_call_to_answering_machine(self):
        """ Voice call to an answering machine.

        1. Make Sure PhoneA attached to voice network.
        2. Call from PhoneA to Storyline
        3. Verify call is in ACTIVE state
        4. Hangup Call from PhoneA

        Raises:
            TestFailure if not success.
        """
        ad = self.android_devices[0]

        if not phone_setup_voice_general(ad.log, ad):
            ad.log.error("Phone Failed to Set Up Properly for Voice.")
            return False
        for iteration in range(3):
            result = True
            ad.log.info("Attempt %d", iteration + 1)
            if not initiate_call(ad.log, ad, self.call_server_number):
                ad.log.error("Call Failed to Initiate")
                result = False
                continue
            if not wait_for_in_call_active(ad, 60, 3):
                ad.log.error("Waiting for Call in Active Failed")
                result = False
            time.sleep(WAIT_TIME_IN_CALL)
            if not is_phone_in_call(ad.log, ad):
                ad.log.error("Call Dropped")
                result = False
            if not hangup_call(ad.log, ad):
                ad.log.error("Call Failed to Hangup")
                result = False
            if result:
                ad.log.info("Call test PASS in iteration %d", iteration + 1)
                return True
            time.sleep(WAIT_TIME_ANDROID_STATE_SETTLING)
        ad.log.info("Call test FAIL in all 3 iterations")
        return False


    @TelephonyBaseTest.tel_test_wrap
    @test_tracker_info(uuid="fca3f9e1-447a-416f-9a9c-50b7161981bf")
    def test_call_mo_voice_general(self):
        """ General voice to voice call.

        1. Make Sure PhoneA attached to voice network.
        2. Make Sure PhoneB attached to voice network.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices

        tasks = [(phone_setup_voice_general, (self.log, ads[0])),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_short_seq(self.log, ads[0], None, None, ads[1],
                                        None, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @TelephonyBaseTest.tel_test_wrap
    @test_tracker_info(uuid="69faeb84-3830-47c0-ad80-dc657381a83b")
    def test_call_mt_voice_general(self):
        """ General voice to voice call.

        1. Make Sure PhoneA attached to voice network.
        2. Make Sure PhoneB attached to voice network.
        3. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneB.
        4. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneA.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices

        tasks = [(phone_setup_voice_general, (self.log, ads[0])),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_short_seq(self.log, ads[1], None, None, ads[0],
                                        None, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="b2de097b-70e1-4242-b555-c1aa0a5acd8c")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_volte_to_volte(self):
        """ VoLTE to VoLTE call test

        1. Make Sure PhoneA is in LTE mode (with VoLTE).
        2. Make Sure PhoneB is in LTE mode (with VoLTE).
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices

        tasks = [(phone_setup_volte, (self.log, ads[0])), (phone_setup_volte,
                                                           (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_short_seq(
            self.log, ads[0], phone_idle_volte, is_phone_in_call_volte, ads[1],
            phone_idle_volte, is_phone_in_call_volte, None,
            WAIT_TIME_IN_CALL_FOR_IMS)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="3c7f5a09-0177-4469-9994-cd5e7dd7c7fe")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_volte_to_volte_7_digit_dialing(self):
        """ VoLTE to VoLTE call test, dial with 7 digit number

        1. Make Sure PhoneA is in LTE mode (with VoLTE).
        2. Make Sure PhoneB is in LTE mode (with VoLTE).
        3. Call from PhoneA to PhoneB by 7-digit phone number, accept on PhoneB.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices
        if ads[0].droid.telephonyGetSimCountryIso() == "ca":
            raise signals.TestSkip("7 digit dialing not supported")
        tasks = [(phone_setup_volte, (self.log, ads[0])), (phone_setup_volte,
                                                           (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        return call_setup_teardown(
            self.log,
            ads[0],
            ads[1],
            ads[0],
            is_phone_in_call_volte,
            is_phone_in_call_volte,
            WAIT_TIME_IN_CALL_FOR_IMS,
            dialing_number_length=7)

    @test_tracker_info(uuid="721ef935-a03c-4d0f-85b9-4753d857162f")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_volte_to_volte_10_digit_dialing(self):
        """ VoLTE to VoLTE call test, dial with 10 digit number

        1. Make Sure PhoneA is in LTE mode (with VoLTE).
        2. Make Sure PhoneB is in LTE mode (with VoLTE).
        3. Call from PhoneA to PhoneB by 10-digit phone number, accept on PhoneB.

        Returns:
            True if pass; False if fail.
        """
        if self.android_devices[0].droid.telephonyGetSimCountryIso() == "ca":
            raise signals.TestSkip("10 digit dialing not supported")

        ads = self.android_devices

        tasks = [(phone_setup_volte, (self.log, ads[0])), (phone_setup_volte,
                                                           (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        if not call_setup_teardown(
            self.log,
            ads[0],
            ads[1],
            ads[0],
            is_phone_in_call_volte,
            is_phone_in_call_volte,
            WAIT_TIME_IN_CALL_FOR_IMS,
            dialing_number_length=10):
            return False

        return True

    @test_tracker_info(uuid="4fd3aa62-2398-4cee-994e-7fc5cadbcbc1")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_volte_to_volte_11_digit_dialing(self):
        """ VoLTE to VoLTE call test, dial with 11 digit number

        1. Make Sure PhoneA is in LTE mode (with VoLTE).
        2. Make Sure PhoneB is in LTE mode (with VoLTE).
        3. Call from PhoneA to PhoneB by 11-digit phone number, accept on PhoneB.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices

        tasks = [(phone_setup_volte, (self.log, ads[0])), (phone_setup_volte,
                                                           (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        return call_setup_teardown(
            self.log,
            ads[0],
            ads[1],
            ads[0],
            is_phone_in_call_volte,
            is_phone_in_call_volte,
            WAIT_TIME_IN_CALL_FOR_IMS,
            dialing_number_length=11)

    @test_tracker_info(uuid="969abdac-6a57-442a-9c40-48199bd8d556")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_volte_to_volte_12_digit_dialing(self):
        """ VoLTE to VoLTE call test, dial with 12 digit number

        1. Make Sure PhoneA is in LTE mode (with VoLTE).
        2. Make Sure PhoneB is in LTE mode (with VoLTE).
        3. Call from PhoneA to PhoneB by 12-digit phone number, accept on PhoneB.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices

        tasks = [(phone_setup_volte, (self.log, ads[0])), (phone_setup_volte,
                                                           (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        return call_setup_teardown(
            self.log,
            ads[0],
            ads[1],
            ads[0],
            is_phone_in_call_volte,
            is_phone_in_call_volte,
            WAIT_TIME_IN_CALL_FOR_IMS,
            dialing_number_length=12)

    @test_tracker_info(uuid="6b13a03d-c9ff-43d7-9798-adbead7688a4")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_volte_to_csfb_3g(self):
        """ VoLTE to CSFB 3G call test

        1. Make Sure PhoneA is in LTE mode (with VoLTE).
        2. Make Sure PhoneB is in LTE mode (without VoLTE).
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])

        tasks = [(phone_setup_volte, (self.log, ads[0])), (phone_setup_csfb,
                                                           (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_short_seq(
            self.log, ads[0], phone_idle_volte, is_phone_in_call_volte, ads[1],
            phone_idle_csfb, is_phone_in_call_csfb, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="38096fdb-324a-4ce0-8836-8bbe713cffc2")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_volte_to_csfb_for_tmo(self):
        """ VoLTE to CSFB 3G call test for TMobile

        1. Make Sure PhoneA is in LTE mode (with VoLTE).
        2. Make Sure PhoneB is in LTE mode (without VoLTE, CSFB to WCDMA/GSM).
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])

        tasks = [(phone_setup_volte, (self.log, ads[0])), (phone_setup_csfb,
                                                           (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_short_seq(self.log, ads[0], phone_idle_volte,
                                        None, ads[1], phone_idle_csfb,
                                        is_phone_in_call_csfb, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="82f9515d-a52b-4dec-93a5-997ffdbca76c")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_volte_to_csfb_1x_long(self):
        """ VoLTE to CSFB 1x call test

        1. Make Sure PhoneA is in LTE mode (with VoLTE).
        2. Make Sure PhoneB is in LTE mode (without VoLTE, CSFB to 1x).
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.
        5. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneB.
        6. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneA.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        # Make Sure PhoneB is CDMA phone.
        if ads[1].droid.telephonyGetPhoneType() != PHONE_TYPE_CDMA:
            self.log.error(
                "PhoneB not cdma phone, can not csfb 1x. Stop test.")
            self.tel_logger.set_result(CallResult("UNAVAILABLE_NETWORK_TYPE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "PhoneB not cdma, cannot csfb 1x."})

        tasks = [(phone_setup_volte, (self.log, ads[0])), (phone_setup_csfb,
                                                           (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_long_seq(
            self.log, ads[0], phone_idle_volte, is_phone_in_call_volte, ads[1],
            phone_idle_csfb, is_phone_in_call_1x, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="2e57fad6-5eaf-4e7d-8353-8aa6f4c52776")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_volte_to_csfb_long(self):
        """ VoLTE to CSFB WCDMA call test

        1. Make Sure PhoneA is in LTE mode (with VoLTE).
        2. Make Sure PhoneB is in LTE mode (without VoLTE, CSFB to WCDMA/GSM).
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.
        5. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneB.
        6. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneA.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        # Make Sure PhoneB is GSM phone.
        if ads[1].droid.telephonyGetPhoneType() != PHONE_TYPE_GSM:
            self.log.error(
                "PhoneB not gsm phone, can not csfb wcdma. Stop test.")
            self.tel_logger.set_result(CallResult("UNAVAILABLE_NETWORK_TYPE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "PhoneB not gsm, cannot csfb wcdma."})

        tasks = [(phone_setup_volte, (self.log, ads[0])), (phone_setup_csfb,
                                                           (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Setup Properly")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Setup Properly"})

        result = two_phone_call_long_seq(
            self.log, ads[0], phone_idle_volte, is_phone_in_call_volte, ads[1],
            phone_idle_csfb, is_phone_in_call_csfb, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="4bab759f-7610-4cec-893c-0a8aed95f70c")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_volte_to_3g(self):
        """ VoLTE to 3G call test

        1. Make Sure PhoneA is in LTE mode (with VoLTE).
        2. Make Sure PhoneB is in 3G mode.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])

        tasks = [(phone_setup_volte, (self.log, ads[0])),
                 (phone_setup_voice_3g, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

        result = two_phone_call_short_seq(
            self.log, ads[0], phone_idle_volte, is_phone_in_call_volte, ads[1],
            phone_idle_3g, is_phone_in_call_3g, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="b394cdc5-d88d-4659-8a26-0e58fde69974")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_volte_to_3g_1x_long(self):
        """ VoLTE to 3G 1x call test

        1. Make Sure PhoneA is in LTE mode (with VoLTE).
        2. Make Sure PhoneB is in 3G 1x mode.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.
        5. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneB.
        6. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneA.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])
        # Make Sure PhoneB is CDMA phone.
        if ads[1].droid.telephonyGetPhoneType() != PHONE_TYPE_CDMA:
            self.log.error("PhoneB not cdma phone, can not 3g 1x. Stop test.")
            self.tel_logger.set_result(CallResult("UNAVAILABLE_NETWORK_TYPE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "PhoneB not cdma phone, can not 3g 1x."})

        tasks = [(phone_setup_volte, (self.log, ads[0])),
                 (phone_setup_voice_3g, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_long_seq(
            self.log, ads[0], phone_idle_volte, is_phone_in_call_volte, ads[1],
            phone_idle_3g, is_phone_in_call_1x, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="b39a74a9-2a89-4c0b-ac4e-71ed9317bd75")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_volte_to_3g_wcdma_long(self):
        """ VoLTE to 3G WCDMA call test

        1. Make Sure PhoneA is in LTE mode (with VoLTE).
        2. Make Sure PhoneB is in 3G WCDMA mode.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.
        5. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneB.
        6. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneA.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])
        # Make Sure PhoneB is GSM phone.
        if ads[1].droid.telephonyGetPhoneType() != PHONE_TYPE_GSM:
            self.log.error(
                "PhoneB not gsm phone, can not 3g wcdma. Stop test.")
            self.tel_logger.set_result(CallResult('UNAVAILABLE_NETWORK_TYPE'))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "PhoneB not gsm phone, can not 3g wcdma."})

        tasks = [(phone_setup_volte, (self.log, ads[0])),
                 (phone_setup_voice_3g, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "PhoneB not gsm phone, can not 3g wcdma."})

        result = two_phone_call_long_seq(
            self.log, ads[0], phone_idle_volte, is_phone_in_call_volte, ads[1],
            phone_idle_3g, is_phone_in_call_wcdma, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="573bbcf1-6cbd-4084-9cb7-e14fb6c9521e")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_volte_to_2g(self):
        """ VoLTE to 2G call test

        1. Make Sure PhoneA is in LTE mode (with VoLTE).
        2. Make Sure PhoneB is in 2G mode.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])

        tasks = [(phone_setup_volte, (self.log, ads[0])),
                 (phone_setup_voice_2g, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_short_seq(
            self.log, ads[0], phone_idle_volte, is_phone_in_call_volte, ads[1],
            phone_idle_2g, is_phone_in_call_2g, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="a4a043c0-f4ba-4405-9262-42c752cc4487")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_epdg_wfc_wifi_only(self):
        """ WiFi Only, WiFi calling to WiFi Calling test

        1. Setup PhoneA WFC mode: WIFI_ONLY.
        2. Setup PhoneB WFC mode: WIFI_ONLY.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Returns:
            True if pass; False if fail.
        """
        return call_epdg_to_epdg_wfc(self.log,
                                     self.android_devices,
                                     False,
                                     WFC_MODE_WIFI_ONLY,
                                     self.wifi_network_ssid,
                                     self.wifi_network_pass)

    @test_tracker_info(uuid="ae171d58-d4c1-43f7-aa93-4860b4b28d53")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_epdg_wfc_wifi_preferred(self):
        """ WiFi Preferred, WiFi calling to WiFi Calling test

        1. Setup PhoneA WFC mode: WIFI_PREFERRED.
        2. Setup PhoneB WFC mode: WIFI_PREFERRED.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Returns:
            True if pass; False if fail.
        """
        return call_epdg_to_epdg_wfc(self.log,
                                     self.android_devices,
                                     False,
                                     WFC_MODE_WIFI_PREFERRED,
                                     self.wifi_network_ssid,
                                     self.wifi_network_pass)

    @test_tracker_info(uuid="ece58857-fedc-49a9-bf10-b76bd78a51f2")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_epdg_wfc_cellular_preferred(self):
        """ Cellular Preferred, WiFi calling to WiFi Calling test

        1. Setup PhoneA WFC mode: CELLULAR_PREFERRED.
        2. Setup PhoneB WFC mode: CELLULAR_PREFERRED.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Raises:
            TestFailure if not success.
        """
        ads = [self.android_devices[0], self.android_devices[1]]
        tasks = [(phone_setup_iwlan_cellular_preferred,
                  (self.log, ads[0], self.wifi_network_ssid,
                   self.wifi_network_pass)),
                 (phone_setup_iwlan_cellular_preferred,
                  (self.log, ads[1], self.wifi_network_ssid,
                   self.wifi_network_pass))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_short_seq(
            self.log, ads[0], None, is_phone_in_call_not_iwlan, ads[1], None,
            is_phone_in_call_not_iwlan, None, WAIT_TIME_IN_CALL_FOR_IMS)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="0d63c250-d9e7-490c-8c48-0a6afbad5f88")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_epdg_apm_wfc_wifi_only(self):
        """ Airplane + WiFi Only, WiFi calling to WiFi Calling test

        1. Setup PhoneA in airplane mode, WFC mode: WIFI_ONLY.
        2. Setup PhoneB in airplane mode, WFC mode: WIFI_ONLY.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Returns:
            True if pass; False if fail.
        """
        return call_epdg_to_epdg_wfc(self.log,
                                     self.android_devices,
                                     True,
                                     WFC_MODE_WIFI_ONLY,
                                     self.wifi_network_ssid,
                                     self.wifi_network_pass)

    @test_tracker_info(uuid="7678e4ee-29c6-4319-93ab-d555501d1876")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_epdg_apm_wfc_wifi_preferred(self):
        """ Airplane + WiFi Preferred, WiFi calling to WiFi Calling test

        1. Setup PhoneA in airplane mode, WFC mode: WIFI_PREFERRED.
        2. Setup PhoneB in airplane mode, WFC mode: WIFI_PREFERRED.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Returns:
            True if pass; False if fail.
        """
        return call_epdg_to_epdg_wfc(self.log,
                                     self.android_devices,
                                     True,
                                     WFC_MODE_WIFI_PREFERRED,
                                     self.wifi_network_ssid,
                                     self.wifi_network_pass)

    @test_tracker_info(uuid="8f5c637e-683a-448d-9443-b2b39626ab19")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_epdg_apm_wfc_cellular_preferred(self):
        """ Airplane + Cellular Preferred, WiFi calling to WiFi Calling test

        1. Setup PhoneA in airplane mode, WFC mode: CELLULAR_PREFERRED.
        2. Setup PhoneB in airplane mode, WFC mode: CELLULAR_PREFERRED.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Returns:
            True if pass; False if fail.
        """
        return call_epdg_to_epdg_wfc(self.log,
                                     self.android_devices,
                                     True,
                                     WFC_MODE_CELLULAR_PREFERRED,
                                     self.wifi_network_ssid,
                                     self.wifi_network_pass)

    @test_tracker_info(uuid="0b51666e-c83c-40b5-ba0f-737e64bc82a2")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_volte_wfc_wifi_only(self):
        """ WiFi Only, WiFi calling to VoLTE test

        1. Setup PhoneA WFC mode: WIFI_ONLY.
        2. Make Sure PhoneB is in LTE mode (with VoLTE enabled).
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], False, WFC_MODE_WIFI_ONLY,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_volte, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_short_seq(
            self.log, ads[0], phone_idle_iwlan, is_phone_in_call_iwlan, ads[1],
            phone_idle_volte, is_phone_in_call_volte, None,
            WAIT_TIME_IN_CALL_FOR_IMS)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="6e0630a9-63b2-4ea1-8ec9-6560f001905c")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_volte_wfc_wifi_preferred(self):
        """ WiFi Preferred, WiFi calling to VoLTE test

        1. Setup PhoneA WFC mode: WIFI_PREFERRED.
        2. Make Sure PhoneB is in LTE mode (with VoLTE enabled).
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], False, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_volte, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_short_seq(
            self.log, ads[0], phone_idle_iwlan, is_phone_in_call_iwlan, ads[1],
            phone_idle_volte, is_phone_in_call_volte, None,
            WAIT_TIME_IN_CALL_FOR_IMS)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="51077985-2229-491f-9a54-1ff53871758c")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_volte_apm_wfc_wifi_only(self):
        """ Airplane + WiFi Only, WiFi calling to VoLTE test

        1. Setup PhoneA in airplane mode, WFC mode: WIFI_ONLY.
        2. Make Sure PhoneB is in LTE mode (with VoLTE enabled).
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], True, WFC_MODE_WIFI_ONLY,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_volte, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_short_seq(
            self.log, ads[0], phone_idle_iwlan, is_phone_in_call_iwlan, ads[1],
            phone_idle_volte, is_phone_in_call_volte, None,
            WAIT_TIME_IN_CALL_FOR_IMS)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="fff9edcd-1ace-4f2d-a09b-06f3eea56cca")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_volte_apm_wfc_wifi_preferred(self):
        """ Airplane + WiFi Preferred, WiFi calling to VoLTE test

        1. Setup PhoneA in airplane mode, WFC mode: WIFI_PREFERRED.
        2. Make Sure PhoneB is in LTE mode (with VoLTE enabled).
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], True, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_volte, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_short_seq(
            self.log, ads[0], phone_idle_iwlan, is_phone_in_call_iwlan, ads[1],
            phone_idle_volte, is_phone_in_call_volte, None,
            WAIT_TIME_IN_CALL_FOR_IMS)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="8591554e-4e38-406c-97bf-8921d5329c47")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_csfb_3g_wfc_wifi_only(self):
        """ WiFi Only, WiFi calling to CSFB 3G test

        1. Setup PhoneA WFC mode: WIFI_ONLY.
        2. Make Sure PhoneB is in LTE mode (with VoLTE disabled).
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Raises:
             TestFailure if not success.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])
        # Turn OFF WiFi for Phone B
        set_wifi_to_default(self.log, ads[1])
        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], False, WFC_MODE_WIFI_ONLY,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_csfb, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_short_seq(
            self.log, ads[0], phone_idle_iwlan, is_phone_in_call_iwlan, ads[1],
            phone_idle_csfb, is_phone_in_call_csfb, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="9711888d-5b1e-4d05-86e9-98f94f46098b")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_csfb_3g_wfc_wifi_preferred(self):
        """ WiFi Preferred, WiFi calling to CSFB 3G test

        1. Setup PhoneA WFC mode: WIFI_PREFERRED.
        2. Make Sure PhoneB is in LTE mode (with VoLTE disabled).
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])
        # Turn OFF WiFi for Phone B
        set_wifi_to_default(self.log, ads[1])
        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], False, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_csfb, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_short_seq(
            self.log, ads[0], phone_idle_iwlan, is_phone_in_call_iwlan, ads[1],
            phone_idle_csfb, is_phone_in_call_csfb, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="902c96a4-858f-43ff-bd56-6d7d27004320")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_csfb_3g_apm_wfc_wifi_only(self):
        """ Airplane + WiFi Only, WiFi calling to CSFB 3G test

        1. Setup PhoneA in airplane mode, WFC mode: WIFI_ONLY.
        2. Make Sure PhoneB is in LTE mode (with VoLTE disabled).
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])
        # Turn OFF WiFi for Phone B
        set_wifi_to_default(self.log, ads[1])
        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], True, WFC_MODE_WIFI_ONLY,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_csfb, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_short_seq(
            self.log, ads[0], phone_idle_iwlan, is_phone_in_call_iwlan, ads[1],
            phone_idle_csfb, is_phone_in_call_csfb, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="362a5396-ebda-4706-a73a-d805e5028fd7")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_csfb_3g_apm_wfc_wifi_preferred(self):
        """ Airplane + WiFi Preferred, WiFi calling to CSFB 3G test

        1. Setup PhoneA in airplane mode, WFC mode: WIFI_PREFERRED.
        2. Make Sure PhoneB is in LTE mode (with VoLTE disabled).
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])
        # Turn OFF WiFi for Phone B
        set_wifi_to_default(self.log, ads[1])
        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], True, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_csfb, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_short_seq(
            self.log, ads[0], phone_idle_iwlan, is_phone_in_call_iwlan, ads[1],
            phone_idle_csfb, is_phone_in_call_csfb, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="647bb859-46bc-4e3e-b6ab-7944d3bbcc26")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_3g_wfc_wifi_only(self):
        """ WiFi Only, WiFi calling to 3G test

        1. Setup PhoneA WFC mode: WIFI_ONLY.
        2. Make Sure PhoneB is in 3G mode.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])
        # Turn OFF WiFi for Phone B
        set_wifi_to_default(self.log, ads[1])
        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], False, WFC_MODE_WIFI_ONLY,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_voice_3g, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_short_seq(
            self.log, ads[0], phone_idle_iwlan, is_phone_in_call_iwlan, ads[1],
            phone_idle_3g, is_phone_in_call_3g, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="3688ea1f-a52d-4a35-9df4-d5ed0985e49b")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_3g_wfc_wifi_preferred(self):
        """ WiFi Preferred, WiFi calling to 3G test

        1. Setup PhoneA WFC mode: WIFI_PREFERRED.
        2. Make Sure PhoneB is in 3G mode.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])
        # Turn OFF WiFi for Phone B
        set_wifi_to_default(self.log, ads[1])
        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], False, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_voice_3g, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_short_seq(
            self.log, ads[0], phone_idle_iwlan, is_phone_in_call_iwlan, ads[1],
            phone_idle_3g, is_phone_in_call_3g, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="f4efc821-fbaf-4ec2-b89b-5a47354344f0")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_3g_apm_wfc_wifi_only(self):
        """ Airplane + WiFi Only, WiFi calling to 3G test

        1. Setup PhoneA in airplane mode, WFC mode: WIFI_ONLY.
        2. Make Sure PhoneB is in 3G mode.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])
        # Turn OFF WiFi for Phone B
        set_wifi_to_default(self.log, ads[1])
        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], True, WFC_MODE_WIFI_ONLY,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_voice_3g, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_short_seq(
            self.log, ads[0], phone_idle_iwlan, is_phone_in_call_iwlan, ads[1],
            phone_idle_3g, is_phone_in_call_3g, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="2b1345b7-3b62-44bd-91ad-9c5a4925b0e1")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_3g_apm_wfc_wifi_preferred(self):
        """ Airplane + WiFi Preferred, WiFi calling to 3G test

        1. Setup PhoneA in airplane mode, WFC mode: WIFI_PREFERRED.
        2. Make Sure PhoneB is in 3G mode.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])
        # Turn OFF WiFi for Phone B
        set_wifi_to_default(self.log, ads[1])
        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], True, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_voice_3g, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_short_seq(
            self.log, ads[0], phone_idle_iwlan, is_phone_in_call_iwlan, ads[1],
            phone_idle_3g, is_phone_in_call_3g, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="7b3fea22-114a-442e-aa12-dde3b6001681")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_csfb_3g_to_csfb_3g(self):
        """ CSFB 3G to CSFB 3G call test

        1. Make Sure PhoneA is in LTE mode, VoLTE disabled.
        2. Make Sure PhoneB is in LTE mode, VoLTE disabled.
        3. Call from PhoneA to PhoneB, accept on PhoneA, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneA, hang up on PhoneB.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])
        # Turn OFF WiFi for Phone B
        set_wifi_to_default(self.log, ads[1])
        tasks = [(phone_setup_csfb, (self.log, ads[0])), (phone_setup_csfb,
                                                          (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_short_seq(
            self.log, ads[0], phone_idle_csfb, is_phone_in_call_csfb, ads[1],
            phone_idle_csfb, is_phone_in_call_csfb, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="91d751ea-40c8-4ffc-b9d3-03d0ad0902bd")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_3g_to_3g(self):
        """ 3G to 3G call test

        1. Make Sure PhoneA is in 3G mode.
        2. Make Sure PhoneB is in 3G mode.
        3. Call from PhoneA to PhoneB, accept on PhoneA, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneA, hang up on PhoneB.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])
        # Turn OFF WiFi for Phone B
        set_wifi_to_default(self.log, ads[1])
        tasks = [(phone_setup_voice_3g, (self.log, ads[0])),
                 (phone_setup_voice_3g, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_short_seq(
            self.log, ads[0], phone_idle_3g, is_phone_in_call_3g, ads[1],
            phone_idle_3g, is_phone_in_call_3g, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="df57c481-010a-4d21-a5c1-5116917871b2")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_volte_to_volte_long(self):
        """ VoLTE to VoLTE call test

        1. Make Sure PhoneA is in LTE mode (with VoLTE).
        2. Make Sure PhoneB is in LTE mode (with VoLTE).
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.
        5. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneB.
        6. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneA.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices

        tasks = [(phone_setup_volte, (self.log, ads[0])), (phone_setup_volte,
                                                           (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_long_seq(
            self.log, ads[0], phone_idle_volte, is_phone_in_call_volte, ads[1],
            phone_idle_volte, is_phone_in_call_volte, None,
            WAIT_TIME_IN_CALL_FOR_IMS)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="b0712d8a-71cf-405f-910c-8592da082660")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_epdg_long_wfc_wifi_only(self):
        """ WiFi Only, WiFi calling to WiFi Calling test

        1. Setup PhoneA WFC mode: WIFI_ONLY.
        2. Setup PhoneB WFC mode: WIFI_ONLY.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.
        5. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneB.
        6. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneA.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices

        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], False, WFC_MODE_WIFI_ONLY,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_iwlan,
                  (self.log, ads[1], False, WFC_MODE_WIFI_ONLY,
                   self.wifi_network_ssid, self.wifi_network_pass))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_long_seq(
            self.log, ads[0], phone_idle_iwlan, is_phone_in_call_iwlan, ads[1],
            phone_idle_iwlan, is_phone_in_call_iwlan, None,
            WAIT_TIME_IN_CALL_FOR_IMS)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="a7293d6c-0fdb-4842-984a-e4c6395fd41d")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_epdg_long_wfc_wifi_preferred(self):
        """ WiFi Preferred, WiFi calling to WiFi Calling test

        1. Setup PhoneA WFC mode: WIFI_PREFERRED.
        2. Setup PhoneB WFC mode: WIFI_PREFERRED.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.
        5. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneB.
        6. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneA.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices

        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], False, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_iwlan,
                  (self.log, ads[1], False, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_long_seq(
            self.log, ads[0], phone_idle_iwlan, is_phone_in_call_iwlan, ads[1],
            phone_idle_iwlan, is_phone_in_call_iwlan, None,
            WAIT_TIME_IN_CALL_FOR_IMS)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="029af2a7-aba4-406b-9095-b32da57a7cdb")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_epdg_long_apm_wfc_wifi_only(self):
        """ Airplane + WiFi Only, WiFi calling to WiFi Calling test

        1. Setup PhoneA in airplane mode, WFC mode: WIFI_ONLY.
        2. Setup PhoneB in airplane mode, WFC mode: WIFI_ONLY.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.
        5. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneB.
        6. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneA.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices

        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], True, WFC_MODE_WIFI_ONLY,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_iwlan,
                  (self.log, ads[1], True, WFC_MODE_WIFI_ONLY,
                   self.wifi_network_ssid, self.wifi_network_pass))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_long_seq(
            self.log, ads[0], phone_idle_iwlan, is_phone_in_call_iwlan, ads[1],
            phone_idle_iwlan, is_phone_in_call_iwlan, None,
            WAIT_TIME_IN_CALL_FOR_IMS)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="3c751d79-7159-4407-a63c-96f835dd6cb0")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_epdg_long_apm_wfc_wifi_preferred(self):
        """ Airplane + WiFi Preferred, WiFi calling to WiFi Calling test

        1. Setup PhoneA in airplane mode, WFC mode: WIFI_PREFERRED.
        2. Setup PhoneB in airplane mode, WFC mode: WIFI_PREFERRED.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.
        5. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneB.
        6. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneA.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices

        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], True, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_iwlan,
                  (self.log, ads[1], True, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_long_seq(
            self.log, ads[0], phone_idle_iwlan, is_phone_in_call_iwlan, ads[1],
            phone_idle_iwlan, is_phone_in_call_iwlan, None,
            WAIT_TIME_IN_CALL_FOR_IMS)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="9deab765-e2da-4826-bae8-ba8755551a1b")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_csfb_3g_to_csfb_3g_long(self):
        """ CSFB 3G to CSFB 3G call test

        1. Make Sure PhoneA is in LTE mode, VoLTE disabled.
        2. Make Sure PhoneB is in LTE mode, VoLTE disabled.
        3. Call from PhoneA to PhoneB, accept on PhoneA, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneA, hang up on PhoneB.
        5. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneB.
        6. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneA.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])
        # Turn OFF WiFi for Phone B
        set_wifi_to_default(self.log, ads[1])
        tasks = [(phone_setup_csfb, (self.log, ads[0])), (phone_setup_csfb,
                                                          (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_long_seq(
            self.log, ads[0], phone_idle_csfb, is_phone_in_call_csfb, ads[1],
            phone_idle_csfb, is_phone_in_call_csfb, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="54768178-818f-4126-9e50-4f49e43a6fd3")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_3g_to_3g_long(self):
        """ 3G to 3G call test

        1. Make Sure PhoneA is in 3G mode.
        2. Make Sure PhoneB is in 3G mode.
        3. Call from PhoneA to PhoneB, accept on PhoneA, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneA, hang up on PhoneB.
        5. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneB.
        6. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneA.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])
        # Turn OFF WiFi for Phone B
        set_wifi_to_default(self.log, ads[1])
        tasks = [(phone_setup_voice_3g, (self.log, ads[0])),
                 (phone_setup_voice_3g, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_long_seq(
            self.log, ads[0], phone_idle_3g, is_phone_in_call_3g, ads[1],
            phone_idle_3g, is_phone_in_call_3g, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_volte_to_volte_loop(self):
        """ Stress test: VoLTE to VoLTE call test

        1. Make Sure PhoneA is in LTE mode (with VoLTE).
        2. Make Sure PhoneB is in LTE mode (with VoLTE).
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.
        5. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneB.
        6. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneA.
        7. Repeat step 3~6.

        Returns:
            True if pass; False if fail.
        """

        # TODO: b/26338422 Make this a parameter
        MINIMUM_SUCCESS_RATE = .95
        ads = self.android_devices

        tasks = [(phone_setup_volte, (self.log, ads[0])), (phone_setup_volte,
                                                           (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        success_count = 0
        fail_count = 0

        for i in range(1, self.stress_test_number + 1):

            if two_phone_call_long_seq(
                    self.log, ads[0], phone_idle_volte, is_phone_in_call_volte,
                    ads[1], phone_idle_volte, is_phone_in_call_volte, None,
                    WAIT_TIME_IN_CALL_FOR_IMS):
                success_count += 1
                result_str = "Succeeded"

            else:
                fail_count += 1
                result_str = "Failed"

            self.log.info("Iteration %s %s. Current: %s / %s passed.", i,
                          result_str, success_count, self.stress_test_number)

        self.log.info("Final Count - Success: %s, Failure: %s - %s%",
                      success_count, fail_count,
                      str(100 * success_count / (success_count + fail_count)))
        if success_count / (
                success_count + fail_count) >= MINIMUM_SUCCESS_RATE:
            return True
        else:
            return False

    @test_tracker_info(uuid="dfa2c1a7-0e9a-42f2-b3ba-7e196df87e1b")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_epdg_loop_wfc_wifi_only(self):
        """ Stress test: WiFi Only, WiFi calling to WiFi Calling test

        1. Setup PhoneA WFC mode: WIFI_ONLY.
        2. Setup PhoneB WFC mode: WIFI_ONLY.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.
        5. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneB.
        6. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneA.
        7. Repeat step 3~6.

        Returns:
            True if pass; False if fail.
        """

        # TODO: b/26338422 Make this a parameter
        MINIMUM_SUCCESS_RATE = .95
        ads = self.android_devices

        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], False, WFC_MODE_WIFI_ONLY,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_iwlan,
                  (self.log, ads[1], False, WFC_MODE_WIFI_ONLY,
                   self.wifi_network_ssid, self.wifi_network_pass))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        success_count = 0
        fail_count = 0

        for i in range(1, self.stress_test_number + 1):

            if two_phone_call_long_seq(
                    self.log, ads[0], phone_idle_iwlan, is_phone_in_call_iwlan,
                    ads[1], phone_idle_iwlan, is_phone_in_call_iwlan, None,
                    WAIT_TIME_IN_CALL_FOR_IMS):
                success_count += 1
                result_str = "Succeeded"

            else:
                fail_count += 1
                result_str = "Failed"

            self.log.info("Iteration %s %s. Current: %s / %s passed.", i,
                          result_str, success_count, self.stress_test_number)

        self.log.info("Final Count - Success: %s, Failure: %s - %s%",
                      success_count, fail_count,
                      str(100 * success_count / (success_count + fail_count)))
        if success_count / (
                success_count + fail_count) >= MINIMUM_SUCCESS_RATE:
            return True
        else:
            return False

    @test_tracker_info(uuid="382f97ad-65d4-4ebb-a31b-aa243e01bce4")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_epdg_loop_wfc_wifi_preferred(self):
        """ Stress test: WiFi Preferred, WiFi Calling to WiFi Calling test

        1. Setup PhoneA WFC mode: WIFI_PREFERRED.
        2. Setup PhoneB WFC mode: WIFI_PREFERRED.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.
        5. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneB.
        6. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneA.
        7. Repeat step 3~6.

        Returns:
            True if pass; False if fail.
        """

        # TODO: b/26338422 Make this a parameter
        MINIMUM_SUCCESS_RATE = .95
        ads = self.android_devices

        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], False, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_iwlan,
                  (self.log, ads[1], False, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        success_count = 0
        fail_count = 0

        for i in range(1, self.stress_test_number + 1):

            if two_phone_call_long_seq(
                    self.log, ads[0], phone_idle_iwlan, is_phone_in_call_iwlan,
                    ads[1], phone_idle_iwlan, is_phone_in_call_iwlan, None,
                    WAIT_TIME_IN_CALL_FOR_IMS):
                success_count += 1
                result_str = "Succeeded"

            else:
                fail_count += 1
                result_str = "Failed"

            self.log.info("Iteration %s %s. Current: %s / %s passed.", i,
                          result_str, success_count, self.stress_test_number)

        self.log.info("Final Count - Success: %s, Failure: %s - %s%",
                      success_count, fail_count,
                      str(100 * success_count / (success_count + fail_count)))
        if success_count / (
                success_count + fail_count) >= MINIMUM_SUCCESS_RATE:
            return True
        else:
            return False

    @test_tracker_info(uuid="c820e2ea-8a14-421c-b608-9074b716f7dd")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_epdg_loop_apm_wfc_wifi_only(self):
        """ Stress test: Airplane + WiFi Only, WiFi Calling to WiFi Calling test

        1. Setup PhoneA in airplane mode, WFC mode: WIFI_ONLY.
        2. Setup PhoneB in airplane mode, WFC mode: WIFI_ONLY.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.
        5. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneB.
        6. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneA.
        7. Repeat step 3~6.

        Returns:
            True if pass; False if fail.
        """

        # TODO: b/26338422 Make this a parameter
        MINIMUM_SUCCESS_RATE = .95
        ads = self.android_devices

        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], True, WFC_MODE_WIFI_ONLY,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_iwlan,
                  (self.log, ads[1], True, WFC_MODE_WIFI_ONLY,
                   self.wifi_network_ssid, self.wifi_network_pass))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        success_count = 0
        fail_count = 0

        for i in range(1, self.stress_test_number + 1):

            if two_phone_call_long_seq(
                    self.log, ads[0], phone_idle_iwlan, is_phone_in_call_iwlan,
                    ads[1], phone_idle_iwlan, is_phone_in_call_iwlan, None,
                    WAIT_TIME_IN_CALL_FOR_IMS):
                success_count += 1
                result_str = "Succeeded"

            else:
                fail_count += 1
                result_str = "Failed"

            self.log.info("Iteration %s %s. Current: %s / %s passed.", i,
                          result_str, success_count, self.stress_test_number)

        self.log.info("Final Count - Success: %s, Failure: %s - %s%",
                      success_count, fail_count,
                      str(100 * success_count / (success_count + fail_count)))
        if success_count / (
                success_count + fail_count) >= MINIMUM_SUCCESS_RATE:
            return True
        else:
            return False

    @test_tracker_info(uuid="3b8cb344-1551-4244-845d-b864501f2fb4")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_to_epdg_loop_apm_wfc_wifi_preferred(self):
        """ Stress test: Airplane + WiFi Preferred, WiFi Calling to WiFi Calling test

        1. Setup PhoneA in airplane mode, WFC mode: WIFI_PREFERRED.
        2. Setup PhoneB in airplane mode, WFC mode: WIFI_PREFERRED.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.
        5. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneB.
        6. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneA.
        7. Repeat step 3~6.

        Returns:
            True if pass; False if fail.
        """

        # TODO: b/26338422 Make this a parameter
        MINIMUM_SUCCESS_RATE = .95
        ads = self.android_devices

        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], True, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_iwlan,
                  (self.log, ads[1], True, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        success_count = 0
        fail_count = 0

        for i in range(1, self.stress_test_number + 1):

            if two_phone_call_long_seq(
                    self.log, ads[0], phone_idle_iwlan, is_phone_in_call_iwlan,
                    ads[1], phone_idle_iwlan, is_phone_in_call_iwlan, None,
                    WAIT_TIME_IN_CALL_FOR_IMS):
                success_count += 1
                result_str = "Succeeded"

            else:
                fail_count += 1
                result_str = "Failed"

            self.log.info("Iteration %s %s. Current: %s / %s passed.", i,
                          result_str, success_count, self.stress_test_number)

        self.log.info("Final Count - Success: %s, Failure: %s - %s%",
                      success_count, fail_count,
                      str(100 * success_count / (success_count + fail_count)))
        if success_count / (
                success_count + fail_count) >= MINIMUM_SUCCESS_RATE:
            return True
        else:
            return False

    @test_tracker_info(uuid="")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_csfb_3g_to_csfb_3g_loop(self):
        """ Stress test: CSFB 3G to CSFB 3G call test

        1. Make Sure PhoneA is in LTE mode, VoLTE disabled.
        2. Make Sure PhoneB is in LTE mode, VoLTE disabled.
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.
        5. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneB.
        6. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneA.
        7. Repeat step 3~6.

        Returns:
            True if pass; False if fail.
        """

        # TODO: b/26338422 Make this a parameter
        MINIMUM_SUCCESS_RATE = .95
        ads = self.android_devices
        self.check_band_support(ads[0])

        tasks = [(phone_setup_csfb, (self.log, ads[0])), (phone_setup_csfb,
                                                          (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        success_count = 0
        fail_count = 0

        for i in range(1, self.stress_test_number + 1):

            if two_phone_call_long_seq(
                    self.log, ads[0], phone_idle_csfb, is_phone_in_call_csfb,
                    ads[1], phone_idle_csfb, is_phone_in_call_csfb, None):
                success_count += 1
                result_str = "Succeeded"

            else:
                fail_count += 1
                result_str = "Failed"

            self.log.info("Iteration %s %s. Current: %s / %s passed.", i,
                          result_str, success_count, self.stress_test_number)

        self.log.info("Final Count - Success: %s, Failure: %s", success_count,
                      fail_count)
        if success_count / (
                success_count + fail_count) >= MINIMUM_SUCCESS_RATE:
            return True
        else:
            return False

    @test_tracker_info(uuid="")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_3g_to_3g_loop(self):
        """ Stress test: 3G to 3G call test

        1. Make Sure PhoneA is in 3G mode
        2. Make Sure PhoneB is in 3G mode
        3. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.
        5. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneB.
        6. Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneA.
        7. Repeat step 3~6.

        Returns:
            True if pass; False if fail.
        """

        # TODO: b/26338422 Make this a parameter
        MINIMUM_SUCCESS_RATE = .95
        ads = self.android_devices
        self.check_band_support(ads[0])

        tasks = [(phone_setup_voice_3g, (self.log, ads[0])),
                 (phone_setup_voice_3g, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        success_count = 0
        fail_count = 0

        for i in range(1, self.stress_test_number + 1):

            if two_phone_call_long_seq(
                    self.log, ads[0], phone_idle_3g, is_phone_in_call_3g,
                    ads[1], phone_idle_3g, is_phone_in_call_3g, None):
                success_count += 1
                result_str = "Succeeded"

            else:
                fail_count += 1
                result_str = "Failed"

            self.log.info("Iteration %s %s. Current: %s / %s passed.", i,
                          result_str, success_count, self.stress_test_number)

        self.log.info("Final Count - Success: %s, Failure: %s", success_count,
                      fail_count)
        if success_count / (
                success_count + fail_count) >= MINIMUM_SUCCESS_RATE:
            return True
        else:
            return False

    @test_tracker_info(uuid="4043c68a-c5d4-4e1d-9010-ef65b205cab1")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_mo_hold_unhold_wfc_wifi_only(self):
        """ WiFi Only, WiFi calling MO call hold/unhold test

        1. Setup PhoneA WFC mode: WIFI_ONLY.
        2. Make sure PhoneB can make/receive voice call.
        3. Call from PhoneA to PhoneB, accept on PhoneB.
        4. Hold and unhold on PhoneA.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices

        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], False, WFC_MODE_WIFI_ONLY,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        ads[0].droid.telecomCallClearCallList()
        if num_active_calls(self.log, ads[0]) != 0:
            ads[0].log.error("Call List is not empty.")
            return False

        self.log.info("Begin MO Call Hold/Unhold Test.")
        if not call_setup_teardown(
                self.log,
                ads[0],
                ads[1],
                ad_hangup=None,
                verify_caller_func=is_phone_in_call_iwlan,
                verify_callee_func=None):
            return False

        if not hold_unhold_test(ads[0].log, ads)[0]:
            self.log.error("Hold/Unhold test fail.")
            return False

        if not hangup_call(self.log, ads[0]):
            self.log.error("Call Hangup Failed")
            return False

        return True

    @test_tracker_info(uuid="0667535e-dcad-49f0-9b4b-fa45d6c75f5b")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_mo_hold_unhold_wfc_wifi_preferred(self):
        """ WiFi Preferred, WiFi calling MO call hold/unhold test

        1. Setup PhoneA WFC mode: WIFI_PREFERRED.
        2. Make sure PhoneB can make/receive voice call.
        3. Call from PhoneA to PhoneB, accept on PhoneB.
        4. Hold and unhold on PhoneA.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices

        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], False, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        ads[0].droid.telecomCallClearCallList()
        if num_active_calls(self.log, ads[0]) != 0:
            ads[0].log.error("Call List is not empty.")
            return False

        self.log.info("Begin MO Call Hold/Unhold Test.")
        if not call_setup_teardown(
                self.log,
                ads[0],
                ads[1],
                ad_hangup=None,
                verify_caller_func=is_phone_in_call_iwlan,
                verify_callee_func=None):
            return False

        if not hold_unhold_test(ads[0].log, ads)[0]:
            self.log.error("Hold/Unhold test fail.")
            return False

        if not hangup_call(self.log, ads[0]):
            self.log.error("Call Hangup Failed")
            return False

        return True

    @test_tracker_info(uuid="cf318b4c-c920-4e80-b73f-2f092c03a144")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_mo_hold_unhold_apm_wfc_wifi_only(self):
        """ Airplane + WiFi Only, WiFi calling MO call hold/unhold test

        1. Setup PhoneA in airplane mode, WFC mode: WIFI_ONLY.
        2. Make sure PhoneB can make/receive voice call.
        3. Call from PhoneA to PhoneB, accept on PhoneB.
        4. Hold and unhold on PhoneA.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices

        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], True, WFC_MODE_WIFI_ONLY,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        ads[0].droid.telecomCallClearCallList()
        if num_active_calls(self.log, ads[0]) != 0:
            ads[0].log.error("Call List is not empty.")
            return False

        self.log.info("Begin MO Call Hold/Unhold Test.")
        if not call_setup_teardown(
                self.log,
                ads[0],
                ads[1],
                ad_hangup=None,
                verify_caller_func=is_phone_in_call_iwlan,
                verify_callee_func=None):
            return False

        if not hold_unhold_test(ads[0].log, ads)[0]:
            self.log.error("Hold/Unhold test fail.")
            return False

        if not hangup_call(self.log, ads[0]):
            self.log.error("Call Hangup Failed")
            return False

        return True

    @test_tracker_info(uuid="ace36801-1e7b-4f06-aa0b-17affc8df069")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_mo_hold_unhold_apm_wfc_wifi_preferred(self):
        """ Airplane + WiFi Preferred, WiFi calling MO call hold/unhold test

        1. Setup PhoneA in airplane mode, WFC mode: WIFI_PREFERRED.
        2. Make sure PhoneB can make/receive voice call.
        3. Call from PhoneA to PhoneB, accept on PhoneB.
        4. Hold and unhold on PhoneA.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices

        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], True, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        ads[0].droid.telecomCallClearCallList()
        if num_active_calls(self.log, ads[0]) != 0:
            ads[0].log.error("Call List is not empty.")
            return False

        self.log.info("Begin MO Call Hold/Unhold Test.")
        if not call_setup_teardown(
                self.log,
                ads[0],
                ads[1],
                ad_hangup=None,
                verify_caller_func=is_phone_in_call_iwlan,
                verify_callee_func=None):
            return False

        if not hold_unhold_test(ads[0].log, ads)[0]:
            self.log.error("Hold/Unhold test fail.")
            return False

        if not hangup_call(self.log, ads[0]):
            self.log.error("Call Hangup Failed")
            return False

        return True

    @test_tracker_info(uuid="2ad32874-0d39-4475-8ae3-d6dccda675f5")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_mt_hold_unhold_wfc_wifi_only(self):
        """ WiFi Only, WiFi calling MT call hold/unhold test

        1. Setup PhoneA WFC mode: WIFI_ONLY.
        2. Make sure PhoneB can make/receive voice call.
        3. Call from PhoneB to PhoneA, accept on PhoneA.
        4. Hold and unhold on PhoneA.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices

        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], False, WFC_MODE_WIFI_ONLY,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        ads[0].droid.telecomCallClearCallList()
        if num_active_calls(self.log, ads[0]) != 0:
            ads[0].log.error("Call List is not empty.")
            return False

        self.log.info("Begin MT Call Hold/Unhold Test.")
        if not call_setup_teardown(
                self.log,
                ads[1],
                ads[0],
                ad_hangup=None,
                verify_caller_func=None,
                verify_callee_func=is_phone_in_call_iwlan):
            return False

        if not hold_unhold_test(ads[0].log, ads)[0]:
            self.log.error("Hold/Unhold test fail.")
            return False

        if not hangup_call(self.log, ads[0]):
            self.log.error("Call Hangup Failed")
            return False

        return True

    @test_tracker_info(uuid="3efd5d59-30ee-45f5-8966-56ce8fadf9a1")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_mt_hold_unhold_wfc_wifi_preferred(self):
        """ WiFi Preferred, WiFi calling MT call hold/unhold test

        1. Setup PhoneA WFC mode: WIFI_PREFERRED.
        2. Make sure PhoneB can make/receive voice call.
        3. Call from PhoneB to PhoneA, accept on PhoneA.
        4. Hold and unhold on PhoneA.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices

        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], False, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        ads[0].droid.telecomCallClearCallList()
        if num_active_calls(self.log, ads[0]) != 0:
            ads[0].log.error("Call List is not empty.")
            return False

        self.log.info("Begin MT Call Hold/Unhold Test.")
        if not call_setup_teardown(
                self.log,
                ads[1],
                ads[0],
                ad_hangup=None,
                verify_caller_func=None,
                verify_callee_func=is_phone_in_call_iwlan):
            return False

        if not hold_unhold_test(ads[0].log, ads)[0]:
            self.log.error("Hold/Unhold test fail.")
            return False

        return True

    @test_tracker_info(uuid="35ed0f89-7435-4d3b-9ebc-c5cdc3f7e32b")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_mt_hold_unhold_apm_wfc_wifi_only(self):
        """ Airplane + WiFi Only, WiFi calling MT call hold/unhold test

        1. Setup PhoneA in airplane mode, WFC mode: WIFI_ONLY.
        2. Make sure PhoneB can make/receive voice call.
        3. Call from PhoneB to PhoneA, accept on PhoneA.
        4. Hold and unhold on PhoneA.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices

        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], True, WFC_MODE_WIFI_ONLY,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        ads[0].droid.telecomCallClearCallList()
        if num_active_calls(self.log, ads[0]) != 0:
            ads[0].log.error("Call List is not empty.")
            return False

        self.log.info("Begin MT Call Hold/Unhold Test.")
        if not call_setup_teardown(
                self.log,
                ads[1],
                ads[0],
                ad_hangup=None,
                verify_caller_func=None,
                verify_callee_func=is_phone_in_call_iwlan):
            return False

        if not hold_unhold_test(ads[0].log, ads)[0]:
            self.log.error("Hold/Unhold test fail.")
            return False

        if not hangup_call(self.log, ads[0]):
            self.log.error("Call Hangup Failed")
            return False

        return True

    @test_tracker_info("37ad003b-6426-42f7-b528-ec7c1842fd18")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_epdg_mt_hold_unhold_apm_wfc_wifi_preferred(self):
        """ Airplane + WiFi Preferred, WiFi calling MT call hold/unhold test

        1. Setup PhoneA in airplane mode, WFC mode: WIFI_PREFERRED.
        2. Make sure PhoneB can make/receive voice call.
        3. Call from PhoneB to PhoneA, accept on PhoneA.
        4. Hold and unhold on PhoneA.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices

        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], True, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        ads[0].droid.telecomCallClearCallList()
        if num_active_calls(self.log, ads[0]) != 0:
            ads[0].log.error("Call List is not empty.")
            return False

        self.log.info("Begin MT Call Hold/Unhold Test.")
        if not call_setup_teardown(
                self.log,
                ads[1],
                ads[0],
                ad_hangup=None,
                verify_caller_func=None,
                verify_callee_func=is_phone_in_call_iwlan):
            return False

        if not hold_unhold_test(ads[0].log, ads)[0]:
            self.log.error("Hold/Unhold test fail.")
            return False

        if not hangup_call(self.log, ads[0]):
            self.log.error("Call Hangup Failed")
            return False

        return True

    @test_tracker_info(uuid="fa37cd37-c30a-4caa-80b4-52507995ec77")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_volte_mo_hold_unhold(self):
        """ VoLTE MO call hold/unhold test

        1. Make Sure PhoneA is in LTE mode (with VoLTE).
        2. Make Sure PhoneB is able to make/receive call.
        3. Call from PhoneA to PhoneB, accept on PhoneB.
        4. Hold and unhold on PhoneA.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices

        tasks = [(phone_setup_volte, (self.log, ads[0])),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        ads[0].droid.telecomCallClearCallList()
        if num_active_calls(self.log, ads[0]) != 0:
            ads[0].log.error("Call List is not empty.")
            return False

        self.log.info("Begin MO Call Hold/Unhold Test.")
        if not call_setup_teardown(
                self.log,
                ads[0],
                ads[1],
                ad_hangup=None,
                verify_caller_func=is_phone_in_call_volte,
                verify_callee_func=None):
            return False

        if not hold_unhold_test(ads[0].log, ads)[0]:
            self.log.error("Hold/Unhold test fail.")
            return False

        if not hangup_call(self.log, ads[0]):
            self.log.error("Call Hangup Failed")
            return False

        return True

    @test_tracker_info(uuid="28a9acb3-83e8-4dd1-82bf-173da8bd2eca")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_volte_mt_hold_unhold(self):
        """ VoLTE MT call hold/unhold test

        1. Make Sure PhoneA is in LTE mode (with VoLTE).
        2. Make Sure PhoneB is able to make/receive call.
        3. Call from PhoneB to PhoneA, accept on PhoneA.
        4. Hold and unhold on PhoneA.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices

        tasks = [(phone_setup_volte, (self.log, ads[0])),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        ads[0].droid.telecomCallClearCallList()
        if num_active_calls(self.log, ads[0]) != 0:
            ads[0].log.error("Call List is not empty.")
            return False

        self.log.info("Begin MT Call Hold/Unhold Test.")
        if not call_setup_teardown(
                self.log,
                ads[1],
                ads[0],
                ad_hangup=None,
                verify_caller_func=None,
                verify_callee_func=is_phone_in_call_volte):
            return False

        if not hold_unhold_test(ads[0].log, ads)[0]:
            self.log.error("Hold/Unhold test fail.")
            return False

        if not hangup_call(self.log, ads[0]):
            self.log.error("Call Hangup Failed")
            return False

        return True

    @test_tracker_info(uuid="ffe724ae-4223-4c15-9fed-9aba17de9a63")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_wcdma_mo_hold_unhold(self):
        """ MO WCDMA hold/unhold test

        1. Make Sure PhoneA is in 3G WCDMA mode.
        2. Make Sure PhoneB is able to make/receive call.
        3. Call from PhoneA to PhoneB, accept on PhoneB.
        4. Hold and unhold on PhoneA.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])
        # make sure PhoneA is GSM phone before proceed.
        if (ads[0].droid.telephonyGetPhoneType() != PHONE_TYPE_GSM):
            ads[0].log.error(
                "Not GSM phone, abort this wcdma hold/unhold test.")
            raise signals.TestSkip(
                "Not GSM phone, abort this wcdma hold/unhold test")

        tasks = [(phone_setup_voice_3g, (self.log, ads[0])),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        ads[0].droid.telecomCallClearCallList()
        if num_active_calls(self.log, ads[0]) != 0:
            ads[0].log.error("Call List is not empty.")
            return False

        self.log.info("Begin MO Call Hold/Unhold Test.")
        if not call_setup_teardown(
                self.log,
                ads[0],
                ads[1],
                ad_hangup=None,
                verify_caller_func=is_phone_in_call_3g,
                verify_callee_func=None):
            return False

        if not hold_unhold_test(ads[0].log, ads)[0]:
            self.log.error("Hold/Unhold test fail.")
            return False

        if not hangup_call(self.log, ads[0]):
            self.log.error("Call Hangup Failed")
            return False

        return True

    @test_tracker_info(uuid="23805165-01ce-4351-83d3-73c9fb3bda76")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_wcdma_mt_hold_unhold(self):
        """ MT WCDMA hold/unhold test

        1. Make Sure PhoneA is in 3G WCDMA mode.
        2. Make Sure PhoneB is able to make/receive call.
        3. Call from PhoneB to PhoneA, accept on PhoneA.
        4. Hold and unhold on PhoneA.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])
        # make sure PhoneA is GSM phone before proceed.
        if (ads[0].droid.telephonyGetPhoneType() != PHONE_TYPE_GSM):
            ads[0].log.error(
                "Not GSM phone, abort this wcdma hold/unhold test.")
            raise signals.TestSkip(
                "Not GSM phone, abort this wcdma hold/unhold test")

        tasks = [(phone_setup_voice_3g, (self.log, ads[0])),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        ads[0].droid.telecomCallClearCallList()
        if num_active_calls(self.log, ads[0]) != 0:
            ads[0].log.error("Call List is not empty.")
            return False

        self.log.info("Begin MT Call Hold/Unhold Test.")
        if not call_setup_teardown(
                self.log,
                ads[1],
                ads[0],
                ad_hangup=None,
                verify_caller_func=None,
                verify_callee_func=is_phone_in_call_3g):
            return False

        if not hold_unhold_test(ads[0].log, ads)[0]:
            self.log.error("Hold/Unhold test fail.")
            return False

        if not hangup_call(self.log, ads[0]):
            self.log.error("Call Hangup Failed")
            return False

        return True

    @test_tracker_info(uuid="08c846c7-1978-4ece-8f2c-731129947699")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_csfb_mo_hold_unhold(self):
        """ MO CSFB WCDMA/GSM hold/unhold test

        1. Make Sure PhoneA is in LTE mode (VoLTE disabled).
        2. Make Sure PhoneB is able to make/receive call.
        3. Call from PhoneA to PhoneB, accept on PhoneB.
        4. Hold and unhold on PhoneA.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices
        # make sure PhoneA is GSM phone before proceed.
        if (ads[0].droid.telephonyGetPhoneType() != PHONE_TYPE_GSM):
            self.log.error("Not GSM phone, abort this wcdma hold/unhold test.")
            raise signals.TestSkip(
                "Not GSM phone, abort this wcdma hold/unhold test")

        tasks = [(phone_setup_csfb, (self.log, ads[0])),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        ads[0].droid.telecomCallClearCallList()
        if num_active_calls(self.log, ads[0]) != 0:
            ads[0].log.error("Call List is not empty.")
            return False

        self.log.info("Begin MO Call Hold/Unhold Test.")
        if not call_setup_teardown(
                self.log,
                ads[0],
                ads[1],
                ad_hangup=None,
                verify_caller_func=is_phone_in_call_csfb,
                verify_callee_func=None):
            return False

        if not hold_unhold_test(ads[0].log, ads)[0]:
            self.log.error("Hold/Unhold test fail.")
            return False

        if not hangup_call(self.log, ads[0]):
            self.log.error("Call Hangup Failed")
            return False

        return True

    @test_tracker_info(uuid="a6405fe6-c732-4ae6-bbae-e912a124f4a2")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_csfb_mt_hold_unhold(self):
        """ MT CSFB WCDMA/GSM hold/unhold test

        1. Make Sure PhoneA is in LTE mode (VoLTE disabled).
        2. Make Sure PhoneB is able to make/receive call.
        3. Call from PhoneB to PhoneA, accept on PhoneA.
        4. Hold and unhold on PhoneA.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices
        # make sure PhoneA is GSM phone before proceed.
        if (ads[0].droid.telephonyGetPhoneType() != PHONE_TYPE_GSM):
            ads[0].log.error(
                "Not GSM phone, abort this wcdma hold/unhold test.")
            raise signals.TestSkip(
                "Not GSM phone, abort this wcdma hold/unhold test")

        tasks = [(phone_setup_csfb, (self.log, ads[0])),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        ads[0].droid.telecomCallClearCallList()
        if num_active_calls(self.log, ads[0]) != 0:
            ads[0].log.error("Call List is not empty.")
            return False

        self.log.info("Begin MT Call Hold/Unhold Test.")
        if not call_setup_teardown(
                self.log,
                ads[1],
                ads[0],
                ad_hangup=None,
                verify_caller_func=None,
                verify_callee_func=is_phone_in_call_csfb):
            return False

        if not hold_unhold_test(ads[0].log, ads)[0]:
            self.log.error("Hold/Unhold test fail.")
            return False

        if not hangup_call(self.log, ads[0]):
            self.log.error("Call Hangup Failed")
            return False

        return True

    @test_tracker_info(uuid="5edc5034-90ef-4113-926f-05407ed60a87")
    @TelephonyBaseTest.tel_test_wrap
    def test_erase_all_pending_voicemail(self):
        """Script for TMO/ATT/SPT phone to erase all pending voice mail.
        This script only works if phone have already set up voice mail options,
        and phone should disable password protection for voice mail.

        1. If phone don't have pending voice message, return True.
        2. Dial voice mail number.
            For TMO, the number is '123'.
            For ATT, the number is phone's number.
            For SPT, the number is phone's number.
        3. Use DTMF to delete all pending voice messages.
        4. Check telephonyGetVoiceMailCount result. it should be 0.

        Returns:
            False if error happens. True is succeed.
        """
        ads = self.android_devices

        tasks = [(phone_setup_voice_general, (self.log, ads[0])),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        return call_voicemail_erase_all_pending_voicemail(
            self.log, self.android_devices[0])

    @test_tracker_info(uuid="c81156a2-089b-4b10-ba80-7afea61d06c6")
    @TelephonyBaseTest.tel_test_wrap
    def test_voicemail_indicator_volte(self):
        """Test Voice Mail notification in LTE (VoLTE enabled).
        This script currently only works for TMO now.

        1. Make sure DUT (ads[0]) in VoLTE mode. Both PhoneB (ads[0]) and DUT idle.
        2. Make call from PhoneB to DUT, reject on DUT.
        3. On PhoneB, leave a voice mail to DUT.
        4. Verify DUT receive voice mail notification.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices

        tasks = [(phone_setup_voice_general, (self.log, ads[1])),
                 (phone_setup_volte, (self.log, ads[0]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False
        if not call_voicemail_erase_all_pending_voicemail(self.log, ads[0]):
            self.log.error("Failed to clear voice mail.")
            return False

        return two_phone_call_leave_voice_mail(self.log, ads[1], None, None,
                                               ads[0], phone_idle_volte)

    @test_tracker_info(uuid="529e12cb-3178-4d2c-b155-d5cfb1eac0c9")
    @TelephonyBaseTest.tel_test_wrap
    def test_voicemail_indicator_lte(self):
        """Test Voice Mail notification in LTE (VoLTE disabled).
        This script currently only works for TMO/ATT/SPT now.

        1. Make sure DUT (ads[1]) in LTE (No VoLTE) mode. Both PhoneB (ads[0]) and DUT idle.
        2. Make call from PhoneB to DUT, reject on DUT.
        3. On PhoneB, leave a voice mail to DUT.
        4. Verify DUT receive voice mail notification.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices

        tasks = [(phone_setup_voice_general, (self.log, ads[0])),
                 (phone_setup_csfb, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False
        if not call_voicemail_erase_all_pending_voicemail(self.log, ads[0]):
            self.log.error("Failed to clear voice mail.")
            return False

        return two_phone_call_leave_voice_mail(self.log, ads[0], None, None,
                                               ads[1], phone_idle_csfb)

    @test_tracker_info(uuid="60cef7dd-f990-4913-af9a-75e9336fc80a")
    @TelephonyBaseTest.tel_test_wrap
    def test_voicemail_indicator_3g(self):
        """Test Voice Mail notification in 3G
        This script currently only works for TMO/ATT/SPT now.

        1. Make sure DUT (ads[0]) in 3G mode. Both PhoneB and DUT idle.
        2. Make call from PhoneB to DUT, reject on DUT.
        3. On PhoneB, leave a voice mail to DUT.
        4. Verify DUT receive voice mail notification.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])

        tasks = [(phone_setup_voice_3g, (self.log, ads[0])),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False
        if not call_voicemail_erase_all_pending_voicemail(self.log, ads[0]):
            self.log.error("Failed to clear voice mail.")
            return False

        return two_phone_call_leave_voice_mail(self.log, ads[1], None, None,
                                               ads[0], phone_idle_3g)

    @test_tracker_info(uuid="e4c83cfa-db60-4258-ab69-15f7de3614b0")
    @TelephonyBaseTest.tel_test_wrap
    def test_voicemail_indicator_2g(self):
        """Test Voice Mail notification in 2G
        This script currently only works for TMO/ATT/SPT now.

        1. Make sure DUT (ads[0]) in 2G mode. Both PhoneB (ads[1]) and DUT idle.
        2. Make call from PhoneB to DUT, reject on DUT.
        3. On PhoneB, leave a voice mail to DUT.
        4. Verify DUT receive voice mail notification.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])

        tasks = [(phone_setup_voice_general, (self.log, ads[1])),
                 (phone_setup_voice_2g, (self.log, ads[0]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False
        if not call_voicemail_erase_all_pending_voicemail(self.log, ads[0]):
            self.log.error("Failed to clear voice mail.")
            return False

        return two_phone_call_leave_voice_mail(self.log, ads[1], None, None,
                                               ads[0], phone_idle_2g)

    @test_tracker_info(uuid="f0cb02fb-a028-43da-9c87-5b21b2f8549b")
    @TelephonyBaseTest.tel_test_wrap
    def test_voicemail_indicator_iwlan(self):
        """Test Voice Mail notification in WiFI Calling
        This script currently only works for TMO now.

        1. Make sure DUT (ads[0]) in WFC mode. Both PhoneB (ads[1]) and DUT idle.
        2. Make call from PhoneB to DUT, reject on DUT.
        3. On PhoneB, leave a voice mail to DUT.
        4. Verify DUT receive voice mail notification.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices

        tasks = [(phone_setup_voice_general, (self.log, ads[1])),
                 (phone_setup_iwlan,
                  (self.log, ads[0], False, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False
        if not call_voicemail_erase_all_pending_voicemail(self.log, ads[0]):
            self.log.error("Failed to clear voice mail.")
            return False

        return two_phone_call_leave_voice_mail(self.log, ads[1], None, None,
                                               ads[0], phone_idle_iwlan)

    @test_tracker_info(uuid="9bd0550e-abfd-436b-912f-571810f973d7")
    @TelephonyBaseTest.tel_test_wrap
    def test_voicemail_indicator_apm_iwlan(self):
        """Test Voice Mail notification in WiFI Calling
        This script currently only works for TMO now.

        1. Make sure DUT (ads[0]) in APM WFC mode. Both PhoneB (ads[1]) and DUT idle.
        2. Make call from PhoneB to DUT, reject on DUT.
        3. On PhoneB, leave a voice mail to DUT.
        4. Verify DUT receive voice mail notification.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices

        tasks = [(phone_setup_voice_general, (self.log, ads[1])),
                 (phone_setup_iwlan,
                  (self.log, ads[0], True, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False
        if not call_voicemail_erase_all_pending_voicemail(self.log, ads[0]):
            self.log.error("Failed to clear voice mail.")
            return False

        return two_phone_call_leave_voice_mail(self.log, ads[1], None, None,
                                               ads[0], phone_idle_iwlan)

    @test_tracker_info(uuid="6bd5cf0f-522e-4e4a-99bf-92ae46261d8c")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_2g_to_2g(self):
        """ Test 2g<->2g call functionality.

        Make Sure PhoneA is in 2g mode.
        Make Sure PhoneB is in 2g mode.
        Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])

        tasks = [(phone_setup_voice_2g, (self.log, ads[0])),
                 (phone_setup_voice_2g, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_short_seq(
            self.log, ads[0], phone_idle_2g, is_phone_in_call_2g, ads[1],
            phone_idle_2g, is_phone_in_call_2g, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="947f3178-735b-4ac2-877c-a06a94972457")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_2g_to_2g_long(self):
        """ Test 2g<->2g call functionality.

        Make Sure PhoneA is in 2g mode.
        Make Sure PhoneB is in 2g mode.
        Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.
        Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneB.
        Call from PhoneB to PhoneA, accept on PhoneA, hang up on PhoneA.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])

        tasks = [(phone_setup_voice_2g, (self.log, ads[0])),
                 (phone_setup_voice_2g, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        result = two_phone_call_long_seq(
            self.log, ads[0], phone_idle_2g, is_phone_in_call_2g, ads[1],
            phone_idle_2g, is_phone_in_call_2g, None)
        self.tel_logger.set_result(result.result_value)
        if not result:
            raise signals.TestFailure("Failed",
                extras={"fail_reason": str(result.result_value)})

    @test_tracker_info(uuid="d109df55-ac2f-493f-9324-9be1d3d7d6d3")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_gsm_mo_hold_unhold(self):
        """ Test GSM call hold/unhold functionality.

        Make Sure PhoneA is in 2g mode (GSM).
        Make Sure PhoneB is able to make/receive call.
        Call from PhoneA to PhoneB, accept on PhoneB, hold and unhold on PhoneA.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])
        # make sure PhoneA is GSM phone before proceed.
        if (ads[0].droid.telephonyGetPhoneType() != PHONE_TYPE_GSM):
            raise signals.TestSkip(
                "Not GSM phone, abort this gsm hold/unhold test")

        tasks = [(phone_setup_voice_2g, (self.log, ads[0])),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        ads[0].droid.telecomCallClearCallList()
        if num_active_calls(self.log, ads[0]) != 0:
            ads[0].log.error("Call List is not empty.")
            return False

        self.log.info("Begin MO Call Hold/Unhold Test.")
        if not call_setup_teardown(
                self.log,
                ads[0],
                ads[1],
                ad_hangup=None,
                verify_caller_func=is_phone_in_call_2g,
                verify_callee_func=None):
            return False

        if not hold_unhold_test(ads[0].log, ads)[0]:
            self.log.error("Hold/Unhold test fail.")
            return False

        return True

    @test_tracker_info(uuid="a8279cda-73b3-470a-8ca7-a331ef99270b")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_gsm_mt_hold_unhold(self):
        """ Test GSM call hold/unhold functionality.

        Make Sure PhoneA is in 2g mode (GSM).
        Make Sure PhoneB is able to make/receive call.
        Call from PhoneB to PhoneA, accept on PhoneA, hold and unhold on PhoneA.

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])
        # make sure PhoneA is GSM phone before proceed.
        if (ads[0].droid.telephonyGetPhoneType() != PHONE_TYPE_GSM):
            self.log.error("Not GSM phone, abort this wcdma hold/unhold test.")
            return False

        tasks = [(phone_setup_voice_2g, (self.log, ads[0])),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        ads[0].droid.telecomCallClearCallList()
        if num_active_calls(self.log, ads[0]) != 0:
            ads[0].log.error("Call List is not empty.")
            return False

        self.log.info("Begin MT Call Hold/Unhold Test.")
        if not call_setup_teardown(
                self.log,
                ads[1],
                ads[0],
                ad_hangup=None,
                verify_caller_func=None,
                verify_callee_func=is_phone_in_call_2g):
            return False

        if not hold_unhold_test(ads[0].log, ads)[0]:
            self.log.error("Hold/Unhold test fail.")
            return False

        return True

    @test_tracker_info(uuid="d0008b51-25ed-414a-9b82-3ffb139a6e0d")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_long_duration_volte(self):
        """ Test call drop rate for VoLTE long duration call.

        Steps:
        1. Setup VoLTE for DUT.
        2. Make VoLTE call from DUT to PhoneB.
        3. For <total_duration> time, check if DUT drop call or not.

        Expected Results:
        DUT should not drop call.

        Returns:
        False if DUT call dropped during test.
        Otherwise True.
        """
        ads = self.android_devices

        tasks = [(phone_setup_volte, (self.log, ads[0])),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        return _test_call_long_duration(self.log, ads,
            is_phone_in_call_volte, self.long_call_duration)

    @test_tracker_info(uuid="d4c1aec0-df05-403f-954c-496faf18605a")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_long_duration_wfc(self):
        """ Test call drop rate for WiFi Calling long duration call.

        Steps:
        1. Setup WFC for DUT.
        2. Make WFC call from DUT to PhoneB.
        3. For <total_duration> time, check if DUT drop call or not.

        Expected Results:
        DUT should not drop call.

        Returns:
        False if DUT call dropped during test.
        Otherwise True.
        """
        ads = self.android_devices

        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], True, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        return _test_call_long_duration(self.log, ads,
            is_phone_in_call_iwlan, self.long_call_duration)

    @test_tracker_info(uuid="bc44f3ca-2616-4024-b959-3a5a85503dfd")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_long_duration_3g(self):
        """ Test call drop rate for 3G long duration call.

        Steps:
        1. Setup 3G for DUT.
        2. Make CS call from DUT to PhoneB.
        3. For <total_duration> time, check if DUT drop call or not.

        Expected Results:
        DUT should not drop call.

        Returns:
        False if DUT call dropped during test.
        Otherwise True.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])

        tasks = [(phone_setup_voice_3g, (self.log, ads[0])),
                 (phone_setup_voice_general, (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        return _test_call_long_duration(self.log, ads,
            is_phone_in_call_3g, self.long_call_duration)

    def _test_call_hangup_while_ringing(self, ad_caller, ad_callee):
        """ Call a phone and verify ringing, then hangup from the originator

        1. Setup PhoneA and PhoneB to ensure voice service.
        2. Call from PhoneA to PhoneB and wait for ringing.
        3. End the call on PhoneA.

        Returns:
            True if pass; False if fail.
        """

        caller_number = ad_caller.telephony['subscription'][
            get_outgoing_voice_sub_id(ad_caller)]['phone_num']
        callee_number = ad_callee.telephony['subscription'][
            get_incoming_voice_sub_id(ad_callee)]['phone_num']

        tasks = [(phone_setup_voice_general, (self.log, ad_caller)),
                 (phone_setup_voice_general, (self.log, ad_callee))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False

        ad_caller.droid.telecomCallClearCallList()
        if num_active_calls(self.log, ad_caller) != 0:
            ad_caller.log.error("Phone has ongoing calls.")
            return False

        if not initiate_call(self.log, ad_caller, callee_number):
            ad_caller.log.error("Phone was unable to initate a call")
            return False

        if not wait_for_ringing_call(self.log, ad_callee, caller_number):
            ad_callee.log.error("Phone never rang.")
            return False

        if not hangup_call(self.log, ad_caller):
            ad_caller.log.error("Unable to hang up the call")
            return False

        return True

    @test_tracker_info(uuid="ef4fb42d-9040-46f2-9626-d0a2e1dd854f")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mo_hangup_while_ringing(self):
        """ Call a phone and verify ringing, then hangup from the originator

        1. Setup PhoneA and PhoneB to ensure voice service.
        2. Call from PhoneA to PhoneB and wait for ringing.
        3. End the call on PhoneA.

        Returns:
            True if pass; False if fail.
        """

        return self._test_call_hangup_while_ringing(self.android_devices[0],
                                                    self.android_devices[1])

    @test_tracker_info(uuid="f514ac72-d551-4e21-b5af-bd87b6cdf34a")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mt_hangup_while_ringing(self):
        """ Call a phone and verify ringing, then hangup from the originator

        1. Setup PhoneA and PhoneB to ensure voice service.
        2. Call from PhoneB to PhoneA and wait for ringing.
        3. End the call on PhoneB.

        Returns:
            True if pass; False if fail.
        """

        return self._test_call_hangup_while_ringing(self.android_devices[1],
                                                    self.android_devices[0])


    @test_tracker_info(uuid="aa40e7e1-e64a-480b-86e4-db2242449555")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mo_voice_general_in_active_data_transfer(self):
        """Test call can be established during active data connection.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in <nw_gen>.
        Starting downloading file from Internet.
        Initiate a MO voice call. Verify call can be established.
        Hangup Voice Call, verify file is downloaded successfully.
        Note: file download will be suspended when call is initiated if voice
              is using voice channel and voice channel and data channel are
              on different RATs.

        Returns:
            True if success.
            False if failed.
        """
        return test_call_setup_in_active_data_transfer(
            self.log,
            self.android_devices,
            rat=None,
            call_direction=DIRECTION_MOBILE_ORIGINATED)

    @test_tracker_info(uuid="d750d66b-2091-4e8d-baa2-084b9d2bbff5")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mt_voice_general_in_active_data_transfer(self):
        """Test call can be established during active data connection.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in <nw_gen>.
        Starting downloading file from Internet.
        Initiate a MT voice call. Verify call can be established.
        Hangup Voice Call, verify file is downloaded successfully.
        Note: file download will be suspended when call is initiated if voice
              is using voice channel and voice channel and data channel are
              on different RATs.

        Returns:
            True if success.
            False if failed.
        """
        return test_call_setup_in_active_data_transfer(
            self.log,
            self.android_devices,
            rat=None,
            call_direction=DIRECTION_MOBILE_TERMINATED)

    @test_tracker_info(uuid="35703e83-b3e6-40af-aeaf-6b983d6205f4")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mo_voice_volte_in_active_data_transfer(self):
        """Test call can be established during active data connection.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in <nw_gen>.
        Starting downloading file from Internet.
        Initiate a MO voice call. Verify call can be established.
        Hangup Voice Call, verify file is downloaded successfully.
        Note: file download will be suspended when call is initiated if voice
              is using voice channel and voice channel and data channel are
              on different RATs.

        Returns:
            True if success.
            False if failed.
        """
        return test_call_setup_in_active_data_transfer(
            self.log,
            self.android_devices,
            rat='volte',
            call_direction=DIRECTION_MOBILE_ORIGINATED)

    @test_tracker_info(uuid="a0f658d9-4212-44db-b3e8-7202f1eec04d")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mt_voice_volte_in_active_data_transfer(self):
        """Test call can be established during active data connection.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in <nw_gen>.
        Starting downloading file from Internet.
        Initiate a MT voice call. Verify call can be established.
        Hangup Voice Call, verify file is downloaded successfully.
        Note: file download will be suspended when call is initiated if voice
              is using voice channel and voice channel and data channel are
              on different RATs.

        Returns:
            True if success.
            False if failed.
        """
        return test_call_setup_in_active_data_transfer(
            self.log,
            self.android_devices,
            rat='volte',
            call_direction=DIRECTION_MOBILE_TERMINATED)

    @test_tracker_info(uuid="e0b264ec-fc29-411e-b018-684b7ff5a37e")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mo_voice_csfb_in_active_data_transfer(self):
        """Test call can be established during active data connection.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in <nw_gen>.
        Starting downloading file from Internet.
        Initiate a MO voice call. Verify call can be established.
        Hangup Voice Call, verify file is downloaded successfully.
        Note: file download will be suspended when call is initiated if voice
              is using voice channel and voice channel and data channel are
              on different RATs.

        Returns:
            True if success.
            False if failed.
        """
        return test_call_setup_in_active_data_transfer(
            self.log,
            self.android_devices,
            rat='csfb',
            call_direction=DIRECTION_MOBILE_ORIGINATED,
            allow_data_transfer_interruption=True)

    @test_tracker_info(uuid="98f04a27-74e1-474d-90d1-a4a45cdb6f5b")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mt_voice_csfb_in_active_data_transfer(self):
        """Test call can be established during active data connection.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in <nw_gen>.
        Starting downloading file from Internet.
        Initiate a MT voice call. Verify call can be established.
        Hangup Voice Call, verify file is downloaded successfully.
        Note: file download will be suspended when call is initiated if voice
              is using voice channel and voice channel and data channel are
              on different RATs.

        Returns:
            True if success.
            False if failed.
        """
        return test_call_setup_in_active_data_transfer(
            self.log,
            self.android_devices,
            rat='csfb',
            call_direction=DIRECTION_MOBILE_TERMINATED,
            allow_data_transfer_interruption=True)

    @test_tracker_info(uuid="359b1ee1-36a6-427b-9d9e-4d77231fcb09")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mo_voice_3g_in_active_data_transfer(self):
        """Test call can be established during active data connection.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in <nw_gen>.
        Starting downloading file from Internet.
        Initiate a MO voice call. Verify call can be established.
        Hangup Voice Call, verify file is downloaded successfully.
        Note: file download will be suspended when call is initiated if voice
              is using voice channel and voice channel and data channel are
              on different RATs.

        Returns:
            True if success.
            False if failed.
        """
        self.check_band_support(self.android_devices[0])
        return test_call_setup_in_active_data_transfer(
            self.log,
            self.android_devices,
            rat='3g',
            call_direction=DIRECTION_MOBILE_ORIGINATED,
            allow_data_transfer_interruption=True)

    @test_tracker_info(uuid="b172bbb4-2d6e-4d83-a381-ebfdf23bc30e")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mt_voice_3g_in_active_data_transfer(self):
        """Test call can be established during active data connection.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in <nw_gen>.
        Starting downloading file from Internet.
        Initiate a MT voice call. Verify call can be established.
        Hangup Voice Call, verify file is downloaded successfully.
        Note: file download will be suspended when call is initiated if voice
              is using voice channel and voice channel and data channel are
              on different RATs.

        Returns:
            True if success.
            False if failed.
        """
        self.check_band_support(self.android_devices[0])
        return test_call_setup_in_active_data_transfer(
            self.log,
            self.android_devices,
            rat='3g',
            call_direction=DIRECTION_MOBILE_TERMINATED,
            allow_data_transfer_interruption=True)

    @test_tracker_info(uuid="f5d9bfd0-0996-4c18-b11e-c6113dc201e2")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mo_voice_2g_in_active_data_transfer(self):
        """Test call can be established during active data connection.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in <nw_gen>.
        Starting downloading file from Internet.
        Initiate a MO voice call. Verify call can be established.
        Hangup Voice Call, verify file is downloaded successfully.
        Note: file download will be suspended when call is initiated if voice
              is using voice channel and voice channel and data channel are
              on different RATs.

        Returns:
            True if success.
            False if failed.
        """
        self.check_band_support(self.android_devices[0])
        return test_call_setup_in_active_data_transfer(
            self.log,
            self.android_devices,
            rat='2g',
            call_direction=DIRECTION_MOBILE_ORIGINATED,
            allow_data_transfer_interruption=True)

    @test_tracker_info(uuid="99cfd1be-b992-48bf-a50e-fc3eec8e5a67")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mt_voice_2g_in_active_data_transfer(self):
        """Test call can be established during active data connection.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in <nw_gen>.
        Starting downloading file from Internet.
        Initiate a MT voice call. Verify call can be established.
        Hangup Voice Call, verify file is downloaded successfully.
        Note: file download will be suspended when call is initiated if voice
              is using voice channel and voice channel and data channel are
              on different RATs.

        Returns:
            True if success.
            False if failed.
        """
        self.check_band_support(self.android_devices[0])
        return test_call_setup_in_active_data_transfer(
            self.log,
            self.android_devices,
            rat='2g',
            call_direction=DIRECTION_MOBILE_TERMINATED,
            allow_data_transfer_interruption=True)

    @test_tracker_info(uuid="12677cf2-40d3-4bb1-8afa-91ebcbd0f862")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mo_voice_wifi_wfc_in_active_data_transfer(self):
        """Test call can be established during active data connection.

        Turn off airplane mode, turn on wfc and wifi.
        Starting downloading file from Internet.
        Initiate a MO voice call. Verify call can be established.
        Hangup Voice Call, verify file is downloaded successfully.

        Returns:
            True if success.
            False if failed.
        """
        if not phone_setup_iwlan(self.log, self.android_devices[0], False,
                                 WFC_MODE_WIFI_PREFERRED,
                                 self.wifi_network_ssid,
                                 self.wifi_network_pass):
            self.android_devices[0].log.error(
                "Failed to setup IWLAN with NON-APM WIFI WFC on")
            return False
        return test_call_setup_in_active_data_transfer(
            self.log,
            self.android_devices,
            rat=None,
            call_direction=DIRECTION_MOBILE_ORIGINATED)

    @test_tracker_info(uuid="84adcc19-43bb-4ea3-9284-7322ab139aac")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mt_voice_wifi_wfc_in_active_data_transfer(self):
        """Test call can be established during active data connection.

        Turn off airplane mode, turn on wfc and wifi.
        Starting downloading file from Internet.
        Initiate a MT voice call. Verify call can be established.
        Hangup Voice Call, verify file is downloaded successfully.

        Returns:
            True if success.
            False if failed.
        """
        if not phone_setup_iwlan(self.log, self.android_devices[0], False,
                                 WFC_MODE_WIFI_PREFERRED,
                                 self.wifi_network_ssid,
                                 self.wifi_network_pass):
            self.android_devices[0].log.error(
                "Failed to setup iwlan with APM off and WIFI and WFC on")
            return False
        return test_call_setup_in_active_data_transfer(
            self.log,
            self.android_devices,
            rat=None,
            call_direction=DIRECTION_MOBILE_TERMINATED)

    @test_tracker_info(uuid="42566255-c33f-406c-abab-932a0aaa01a8")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mo_voice_apm_wifi_wfc_in_active_data_transfer(self):
        """Test call can be established during active data connection.

        Turn on wifi-calling, airplane mode and wifi.
        Starting downloading file from Internet.
        Initiate a MO voice call. Verify call can be established.
        Hangup Voice Call, verify file is downloaded successfully.

        Returns:
            True if success.
            False if failed.
        """
        carrier = self.get_carrier_name(self.android_devices[0])
        if carrier == CARRIER_VZW:
            wfc = WFC_MODE_CELLULAR_PREFERRED
        else:
            wfc = WFC_MODE_WIFI_PREFERRED
        if not phone_setup_iwlan(self.log, self.android_devices[0], True,
                                 wfc,
                                 self.wifi_network_ssid,
                                 self.wifi_network_pass):
            self.android_devices[0].log.error(
                "Failed to setup iwlan with APM, WIFI and WFC on")
            return False
        return test_call_setup_in_active_data_transfer(
            self.log,
            self.android_devices,
            rat=None,
            call_direction=DIRECTION_MOBILE_ORIGINATED)

    @test_tracker_info(uuid="fbf52f60-449b-46f2-9486-36d338a1b070")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mt_voice_apm_wifi_wfc_in_active_data_transfer(self):
        """Test call can be established during active data connection.

        Turn on wifi-calling, airplane mode and wifi.
        Starting downloading file from Internet.
        Initiate a MT voice call. Verify call can be established.
        Hangup Voice Call, verify file is downloaded successfully.

        Returns:
            True if success.
            False if failed.
        """
        carrier = self.get_carrier_name(self.android_devices[0])
        if carrier == CARRIER_VZW:
            wfc = WFC_MODE_CELLULAR_PREFERRED
        else:
            wfc = WFC_MODE_WIFI_PREFERRED
        if not phone_setup_iwlan(self.log, self.android_devices[0], True,
                                 wfc,
                                 self.wifi_network_ssid,
                                 self.wifi_network_pass):
            self.android_devices[0].log.error(
                "Failed to setup iwlan with APM, WIFI and WFC on")
            return False
        return test_call_setup_in_active_data_transfer(
            self.log,
            self.android_devices,
            rat=None,
            call_direction=DIRECTION_MOBILE_TERMINATED)

    @test_tracker_info(uuid="d1bf0739-ffb7-4bf8-ab94-570619f812a8")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mo_voice_apm_wifi_in_active_data_transfer_cellular(self):
        """Test call can be established during active data connection.

        Turn on wifi, airplane mode and wifi.
        Starting downloading file from Internet.
        Initiate a MO voice call. Verify call can be established.
        Hangup Voice Call, verify file is downloaded successfully.

        Returns:
            True if success.
            False if failed.
        """
        if not phone_setup_iwlan(self.log,
                                 self.android_devices[0],
                                 True,
                                 WFC_MODE_CELLULAR_PREFERRED,
                                 self.wifi_network_ssid,
                                 self.wifi_network_pass):
            self.android_devices[0].log.error(
                "Failed to setup iwlan with APM, WIFI")
            return False
        return test_call_setup_in_active_data_transfer(
            self.log,
            self.android_devices,
            rat=None,
            call_direction=DIRECTION_MOBILE_ORIGINATED)

    @test_tracker_info(uuid="76b2cdaf-b783-4c1a-b91b-207f82ffa816")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mt_voice_apm_wifi_in_active_data_transfer_cellular(self):
        """Test call can be established during active data connection.

        Turn on wifi, airplane mode and wifi.
        Starting downloading file from Internet.
        Initiate a MT voice call. Verify call can be established.
        Hangup Voice Call, verify file is downloaded successfully.

        Returns:
            True if success.
            False if failed.
        """
        if not phone_setup_iwlan(self.log,
                                 self.android_devices[0],
                                 True,
                                 WFC_MODE_CELLULAR_PREFERRED,
                                 self.wifi_network_ssid,
                                 self.wifi_network_pass):
            self.android_devices[0].log.error(
                "Failed to setup iwlan with APM, WIFI and WFC on")
            return False
        return test_call_setup_in_active_data_transfer(
            self.log,
            self.android_devices,
            rat=None,
            call_direction=DIRECTION_MOBILE_TERMINATED)

    @test_tracker_info(uuid="1dc9f03f-1b6c-4c17-993b-3acafdc26ea3")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mo_voice_general_in_active_youtube_video(self):
        """Test call can be established during active youtube video.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in <nw_gen>.
        Starting an youtube video.
        Initiate a MO voice call. Verify call can be established.

        Returns:
            True if success.
            False if failed.
        """
        return test_call_setup_in_active_youtube_video(
            self.log,
            self.android_devices,
            rat=None,
            call_direction=DIRECTION_MOBILE_ORIGINATED)

    @test_tracker_info(uuid="32bc8fab-a0b9-4d47-8afb-940d1fdcde02")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mt_voice_general_in_active_youtube_video(self):
        """Test call can be established during active youtube video.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in <nw_gen>.
        Starting an youtube video.
        Initiate a MT voice call. Verify call can be established.

        Returns:
            True if success.
            False if failed.
        """
        return test_call_setup_in_active_youtube_video(
            self.log,
            self.android_devices,
            rat=None,
            call_direction=DIRECTION_MOBILE_TERMINATED)

    @test_tracker_info(uuid="72204212-e0c8-4447-be3f-ae23b2a63a1c")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mo_voice_volte_in_active_youtube_video(self):
        """Test call can be established during active youtube video.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in <nw_gen>.
        Starting an youtube video.
        Initiate a MO voice call. Verify call can be established.

        Returns:
            True if success.
            False if failed.
        """
        return test_call_setup_in_active_youtube_video(
            self.log,
            self.android_devices,
            rat='volte',
            call_direction=DIRECTION_MOBILE_ORIGINATED)

    @test_tracker_info(uuid="84cd3ab9-a2b2-4ef9-b531-ee6201bec128")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mt_voice_volte_in_active_youtube_video(self):
        """Test call can be established during active youtube video.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in <nw_gen>.
        Starting an youtube video.
        Initiate a MT voice call. Verify call can be established.

        Returns:
            True if success.
            False if failed.
        """
        return test_call_setup_in_active_youtube_video(
            self.log,
            self.android_devices,
            rat='volte',
            call_direction=DIRECTION_MOBILE_TERMINATED)

    @test_tracker_info(uuid="a8dca8d3-c44c-40a6-be56-931b4be5499b")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mo_voice_csfb_in_active_youtube_video(self):
        """Test call can be established during active youbube video.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in <nw_gen>.
        Starting an youtube video.
        Initiate a MO voice call. Verify call can be established.

        Returns:
            True if success.
            False if failed.
        """
        return test_call_setup_in_active_youtube_video(
            self.log,
            self.android_devices,
            rat='csfb',
            call_direction=DIRECTION_MOBILE_ORIGINATED)

    @test_tracker_info(uuid="d11f7263-f51d-4ea3-916a-0df4f52023ce")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mt_voice_csfb_in_active_youtube_video(self):
        """Test call can be established during active youtube video.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in <nw_gen>.
        Starting an youtube video.
        Initiate a MT voice call. Verify call can be established.

        Returns:
            True if success.
            False if failed.
        """
        return test_call_setup_in_active_youtube_video(
            self.log,
            self.android_devices,
            rat='csfb',
            call_direction=DIRECTION_MOBILE_TERMINATED)

    @test_tracker_info(uuid="676378b4-94b7-4ad7-8242-7ccd2bf1efba")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mo_voice_3g_in_active_youtube_video(self):
        """Test call can be established during active youtube video.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in <nw_gen>.
        Starting an youtube video.
        Initiate a MO voice call. Verify call can be established.

        Returns:
            True if success.
            False if failed.
        """
        self.check_band_support(self.android_devices[0])
        return test_call_setup_in_active_youtube_video(
            self.log,
            self.android_devices,
            rat='3g',
            call_direction=DIRECTION_MOBILE_ORIGINATED)

    @test_tracker_info(uuid="6216fc6d-2aa2-4eb9-90e2-5791cb31c12e")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mt_voice_3g_in_active_youtube_video(self):
        """Test call can be established during active youtube video.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in <nw_gen>.
        Starting youtube video.
        Initiate a MT voice call. Verify call can be established.

        Returns:
            True if success.
            False if failed.
        """
        self.check_band_support(self.android_devices[0])
        return test_call_setup_in_active_youtube_video(
            self.log,
            self.android_devices,
            rat='3g',
            call_direction=DIRECTION_MOBILE_TERMINATED)

    @test_tracker_info(uuid="58ec9783-6f8e-49f6-8dae-9dd33108b6f9")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mo_voice_2g_in_active_youtube_video(self):
        """Test call can be established during active youtube video.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in <nw_gen>.
        Starting youtube video.
        Initiate a MO voice call. Verify call can be established.

        Returns:
            True if success.
            False if failed.
        """
        self.check_band_support(self.android_devices[0])
        return test_call_setup_in_active_youtube_video(
            self.log,
            self.android_devices,
            rat='2g',
            call_direction=DIRECTION_MOBILE_ORIGINATED)

    @test_tracker_info(uuid="e8ba7c0c-48a3-4fc6-aa34-a2e1c570521a")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mt_voice_2g_in_active_youtube_video(self):
        """Test call can be established during active youtube video.

        Turn off airplane mode, disable WiFi, enable Cellular Data.
        Make sure phone in <nw_gen>.
        Starting an youtube video.
        Initiate a MT voice call. Verify call can be established.

        Returns:
            True if success.
            False if failed.
        """
        self.check_band_support(self.android_devices[0])
        return test_call_setup_in_active_youtube_video(
            self.log,
            self.android_devices,
            rat='2g',
            call_direction=DIRECTION_MOBILE_TERMINATED)

    @test_tracker_info(uuid="eb8971c1-b34a-430f-98df-0d4554c7ab12")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mo_voice_wifi_wfc_in_active_youtube_video(self):
        """Test call can be established during active youtube video.

        Turn off airplane mode, turn on wfc and wifi.
        Starting youtube video.
        Initiate a MO voice call. Verify call can be established.

        Returns:
            True if success.
            False if failed.
        """
        return test_call_setup_in_active_youtube_video(
            self.log,
            self.android_devices,
            rat="wfc",
            wfc_mode=WFC_MODE_WIFI_PREFERRED,
            wifi_ssid=self.wifi_network_ssid,
            wifi_pwd=self.wifi_network_pass,
            call_direction=DIRECTION_MOBILE_ORIGINATED)

    @test_tracker_info(uuid="275a93d6-1f39-40c8-893f-ff77afd09e54")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mt_voice_wifi_wfc_in_active_youtube_video(self):
        """Test call can be established during active youtube_video.

        Turn off airplane mode, turn on wfc and wifi.
        Starting an youtube video.
        Initiate a MT voice call. Verify call can be established.

        Returns:
            True if success.
            False if failed.
        """
        return test_call_setup_in_active_youtube_video(
            self.log,
            self.android_devices,
            rat="wfc",
            wfc_mode=WFC_MODE_WIFI_PREFERRED,
            wifi_ssid=self.wifi_network_ssid,
            wifi_pwd=self.wifi_network_pass,
            call_direction=DIRECTION_MOBILE_TERMINATED)

    @test_tracker_info(uuid="ea087709-d4df-4223-b80c-1b33bacbd5a2")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mo_voice_apm_wifi_wfc_in_active_youtube_video(self):
        """Test call can be established during active youtube video.

        Turn on wifi-calling, airplane mode and wifi.
        Starting an youtube video.
        Initiate a MO voice call. Verify call can be established.

        Returns:
            True if success.
            False if failed.
        """
        carrier = self.get_carrier_name(self.android_devices[0])
        if carrier == CARRIER_VZW:
            wfc = WFC_MODE_CELLULAR_PREFERRED
        else:
            wfc = WFC_MODE_WIFI_PREFERRED

        return test_call_setup_in_active_youtube_video(
            self.log,
            self.android_devices,
            rat="wfc",
            is_airplane_mode=True,
            wfc_mode=wfc,
            wifi_ssid=self.wifi_network_ssid,
            wifi_pwd=self.wifi_network_pass,
            call_direction=DIRECTION_MOBILE_ORIGINATED)

    @test_tracker_info(uuid="44cc14e0-60c7-4fdb-ad26-31fdc4e52aaf")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mt_voice_apm_wifi_wfc_in_active_youtube_video(self):
        """Test call can be established during active youtube video.

        Turn on wifi-calling, airplane mode and wifi.
        Starting youtube video.
        Initiate a MT voice call. Verify call can be established.

        Returns:
            True if success.
            False if failed.
        """
        carrier = self.get_carrier_name(self.android_devices[0])
        if carrier == CARRIER_VZW:
            wfc = WFC_MODE_CELLULAR_PREFERRED
        else:
            wfc = WFC_MODE_WIFI_PREFERRED

        return test_call_setup_in_active_youtube_video(
            self.log,
            self.android_devices,
            rat="wfc",
            is_airplane_mode=True,
            wfc_mode=wfc,
            wifi_ssid=self.wifi_network_ssid,
            wifi_pwd=self.wifi_network_pass,
            call_direction=DIRECTION_MOBILE_TERMINATED)

    @test_tracker_info(uuid="e115e8a6-25bf-41fc-aeb8-8f4c922c50e4")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mo_voice_apm_wifi_wfc_in_active_youtube_video_cellular(self):
        """Test call can be established during active youtube video.

        Turn on wifi-calling, airplane mode and wifi.
        Starting an youtube video.
        Initiate a MO voice call. Verify call can be established.

        Returns:
            True if success.
            False if failed.
        """
        return test_call_setup_in_active_youtube_video(
            self.log,
            self.android_devices,
            rat="wfc",
            is_airplane_mode=True,
            wfc_mode=WFC_MODE_CELLULAR_PREFERRED,
            wifi_ssid=self.wifi_network_ssid,
            wifi_pwd=self.wifi_network_pass,
            call_direction=DIRECTION_MOBILE_ORIGINATED)

    @test_tracker_info(uuid="d754d3dd-0b02-4f13-bc65-fdafa254196b")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mt_voice_apm_wifi_wfc_in_active_youtube_video_cellular(self):
        """Test call can be established during active youtube video.

        Turn on wifi-calling, airplane mode and wifi.
        Starting youtube video.
        Initiate a MT voice call. Verify call can be established.

        Returns:
            True if success.
            False if failed.
        """
        return test_call_setup_in_active_youtube_video(
            self.log,
            self.android_devices,
            rat="wfc",
            is_airplane_mode=True,
            wfc_mode=WFC_MODE_CELLULAR_PREFERRED,
            wifi_ssid=self.wifi_network_ssid,
            wifi_pwd=self.wifi_network_pass,
            call_direction=DIRECTION_MOBILE_TERMINATED)

    @test_tracker_info(uuid="88822edf-4c4a-4bc4-9280-2f27ee9e28d5")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mo_voice_apm_wifi_in_active_youtube_video_cellular(self):
        """Test call can be established during active youtube video.

        Turn on wifi, Cellular Preferred, airplane mode and wifi.
        Starting an youtube video.
        Initiate a MO voice call. Verify call can be established.

        Returns:
            True if success.
            False if failed.
        """
        return test_call_setup_in_active_youtube_video(
            self.log,
            self.android_devices,
            rat="wfc",
            is_airplane_mode=True,
            wfc_mode=WFC_MODE_CELLULAR_PREFERRED,
            wifi_ssid=self.wifi_network_ssid,
            wifi_pwd=self.wifi_network_pass,
            call_direction=DIRECTION_MOBILE_ORIGINATED)

    @test_tracker_info(uuid="c4b066b0-3cfd-4831-9c61-5d6b132648c4")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_mt_voice_apm_wifi_in_active_youtube_video_cellular(self):
        """Test call can be established during active youtube video.

        Turn on cellular calling, airplane mode and wifi.
        Starting youtube video.
        Initiate a MT voice call. Verify call can be established.

        Returns:
            True if success.
            False if failed.
        """
        return test_call_setup_in_active_youtube_video(
            self.log,
            self.android_devices,
            rat="wfc",
            is_airplane_mode=True,
            wfc_mode=WFC_MODE_CELLULAR_PREFERRED,
            wifi_ssid=self.wifi_network_ssid,
            wifi_pwd=self.wifi_network_pass,
            call_direction=DIRECTION_MOBILE_TERMINATED)

    @test_tracker_info(uuid="f367de12-1fd8-488d-816f-091deaacb791")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_wfc_wifi_preferred_after_mobile_data_usage_limit_reached(
            self):
        """ WiFi Preferred, WiFi calling test after data limit reached

        1. Set the data limit to the current usage
        2. Setup PhoneA WFC mode: WIFI_PREFERRED.
        3. Make Sure PhoneB is in general mode.
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        5. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Raises:
            TestFailure is not success.
        """
        ads = self.android_devices
        self.check_band_support(ads[0])
        try:
            subscriber_id = ads[0].droid.telephonyGetSubscriberId()
            data_usage = get_mobile_data_usage(ads[0], subscriber_id)
            set_mobile_data_usage_limit(ads[0], data_usage, subscriber_id)

            # Turn OFF WiFi for Phone B
            set_wifi_to_default(self.log, ads[1])
            tasks = [(phone_setup_iwlan,
                      (self.log, ads[0], False, WFC_MODE_WIFI_PREFERRED,
                       self.wifi_network_ssid, self.wifi_network_pass)),
                     (phone_setup_voice_general, (self.log, ads[1]))]
            if not multithread_func(self.log, tasks):
                self.log.error("Phone Failed to Set Up Properly.")
                self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
                raise signals.TestFailure("Failed",
                    extras={"fail_reason": "Phone Failed to Set Up Properly."})

            result = two_phone_call_short_seq(
                self.log, ads[0], phone_idle_iwlan, is_phone_in_call_iwlan,
                ads[1], phone_idle_3g, is_phone_in_call_3g, None)
            self.tel_logger.set_result(result.result_value)
            if not result:
                raise signals.TestFailure("Failed",
                    extras={"fail_reason": str(result.result_value)})
        finally:
            remove_mobile_data_usage_limit(ads[0], subscriber_id)

    @test_tracker_info(uuid="af943c7f-2b42-408f-b8a3-2d360a7483f7")
    @TelephonyBaseTest.tel_test_wrap
    def test_call_volte_after_mobile_data_usage_limit_reached(self):
        """ VoLTE to VoLTE call test after mobile data usage limit reached

        1. Set the data limit to the current usage
        2. Make Sure PhoneA is in LTE mode (with VoLTE).
        3. Make Sure PhoneB is in LTE mode (with VoLTE).
        4. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneA.
        5. Call from PhoneA to PhoneB, accept on PhoneB, hang up on PhoneB.

        Raises:
            TestFailure if not success.
        """
        ads = self.android_devices
        try:
            subscriber_id = ads[0].droid.telephonyGetSubscriberId()
            data_usage = get_mobile_data_usage(ads[0], subscriber_id)
            set_mobile_data_usage_limit(ads[0], data_usage, subscriber_id)

            tasks = [(phone_setup_volte, (self.log, ads[0])),
                     (phone_setup_volte, (self.log, ads[1]))]
            if not multithread_func(self.log, tasks):
                self.log.error("Phone Failed to Set Up Properly.")
                self.tel_logger.set_result(CallResult("CALL_SETUP_FAILURE"))
                raise signals.TestFailure("Failed",
                    extras={"fail_reason": "Phone Failed to Set Up Properly."})

            result = two_phone_call_short_seq(
                self.log, ads[0], phone_idle_volte, is_phone_in_call_volte,
                ads[1], phone_idle_volte, is_phone_in_call_volte, None,
                WAIT_TIME_IN_CALL_FOR_IMS)
            self.tel_logger.set_result(result.result_value)
            if not result:
                raise signals.TestFailure("Failed",
                    extras={"fail_reason": str(result.result_value)})
        finally:
            remove_mobile_data_usage_limit(ads[0], subscriber_id)

    @test_tracker_info(uuid="7955f1ae-84b1-4c33-9e59-af930605672a")
    @TelephonyBaseTest.tel_test_wrap
    def test_volte_in_call_wifi_toggling(self):
        """ General voice to voice call.

        1. Make Sure PhoneA in VoLTE.
        2. Make Sure PhoneB in VoLTE.
        3. Call from PhoneA to PhoneB.
        4. Toggling Wifi connnection in call.
        5. Verify call is active.
        6. Hung up the call on PhoneA

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices

        tasks = [(phone_setup_volte, (self.log, ads[0])), (phone_setup_volte,
                                                           (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False
        return test_wifi_cell_switching_in_call(
            self.log,
            ads,
            self.wifi_network_ssid,
            self.wifi_network_pass,
            verify_caller_func=is_phone_in_call_volte,
            verify_callee_func=is_phone_in_call_volte)

    @test_tracker_info(uuid="8a853186-cdff-4078-930a-6c619ea89183")
    @TelephonyBaseTest.tel_test_wrap
    def test_wfc_in_call_wifi_toggling(self):
        """ General voice to voice call. TMO Only Test

        1. Make Sure PhoneA in wfc with APM off.
        2. Make Sure PhoneB in Voice Capable.
        3. Call from PhoneA to PhoneB.
        4. Toggling Wifi connection in call.
        5. Verify call is active.
        6. Hung up the call on PhoneA

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices

        if not phone_setup_volte(self.log, ads[0]):
            return False

        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], False, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass)),
                 (phone_setup_voice_general, (self.log, ads[1]))]

        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False
        return test_wifi_cell_switching_in_call(
            self.log,
            ads,
            self.wifi_network_ssid,
            self.wifi_network_pass,
            verify_caller_func=is_phone_in_call_iwlan)

    @test_tracker_info(uuid="187bf7b5-d122-4914-82c0-b0709272ee12")
    @TelephonyBaseTest.tel_test_wrap
    def test_csfb_in_call_wifi_toggling(self):
        """ General voice to voice call.

        1. Make Sure PhoneA in CSFB.
        2. Make Sure PhoneB in CSFB.
        3. Call from PhoneA to PhoneB.
        4. Toggling Wifi connection in call.
        5. Verify call is active.
        6. Hung up the call on PhoneA

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices

        tasks = [(phone_setup_csfb, (self.log, ads[0])), (phone_setup_csfb,
                                                          (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            return False
        return test_wifi_cell_switching_in_call(
            self.log,
            ads,
            self.wifi_network_ssid,
            self.wifi_network_pass,
            verify_caller_func=is_phone_in_call_csfb,
            verify_callee_func=is_phone_in_call_csfb)

    @test_tracker_info(uuid="df555d9f-30e6-47f9-9e9f-9814e6892857")
    @TelephonyBaseTest.tel_test_wrap
    def test_wfc_lte_call_handover(self):
        """ WFC to lte handover.

        1. Make a voice call over wifi.
        2. Turn off Wifi.
        3. Call should handover from Wifi to LTE.
        4. Verify call is active.
        5. Hung up the call on PhoneA

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices

        tasks = [(phone_setup_volte, (self.log, ads[0])), (phone_setup_volte,
                                                           (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})


        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], False, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass))]

        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        ad_caller = ads[0]
        ad_callee = ads[1]
        caller_number = get_phone_number(self.log, ad_caller)
        callee_number = get_phone_number(self.log, ad_callee)

        try:
            # Make MO/MT call.
            if not initiate_call(self.log, ad_caller, callee_number):
                raise signals.TestFailure("Failed to initiate call")
            if not wait_and_answer_call(self.log, ad_callee, caller_number):
                raise signals.TestFailure("Answer call falied")
            if not self._is_phone_in_call_iwlan():
                raise signals.TestFailure("Phone call not in Iwlan ")
            time.sleep(15)
            # Turn off the wifi and wait call to handover.
            wifi_toggle_state(self.log, self.android_devices[0], False)
            time.sleep(15)
            if not self.is_phone_in_call_volte():
                raise signals.TestFailure("WFC handover failed, call disconnected ")

            else:
                self.log.info("Handover Successful")

            if is_phone_in_call(self.log, ads[0]):
                # hangup call
                if not hangup_call(self.log, ads[0]):
                    raise signals.TestFailure("hangup_call fail.")

            else:
                raise signals.TestFailure("Unexpected call drop.")


        except Exception as e:
                self.log.error("Exception error %s", str(e))
                return False
        return True

    @test_tracker_info(uuid="331ff54c-ee36-4f59-9c3c-24faf41b1383")
    @TelephonyBaseTest.tel_test_wrap
    def test_lte_wfc_call_handover(self):
        """ LTE to WFC handover.

        1. Make a voice call over LTE.
        2. Turn on Wifi.
        3. Call should handover from LTE to Wifi.
        4. Verify call is active.
        5. Hung up the call on PhoneA

        Returns:
            True if pass; False if fail.
        """
        ads = self.android_devices

        tasks = [(phone_setup_volte, (self.log, ads[0])), (phone_setup_volte,
                                                           (self.log, ads[1]))]
        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})


        tasks = [(phone_setup_iwlan,
                  (self.log, ads[0], False, WFC_MODE_WIFI_PREFERRED,
                   self.wifi_network_ssid, self.wifi_network_pass))]

        if not multithread_func(self.log, tasks):
            self.log.error("Phone Failed to Set Up Properly.")
            raise signals.TestFailure("Failed",
                extras={"fail_reason": "Phone Failed to Set Up Properly."})

        ad_caller = ads[0]
        ad_callee = ads[1]
        caller_number = get_phone_number(self.log, ad_caller)
        callee_number = get_phone_number(self.log, ad_callee)

        try:
            # Turn off the wifi and make a call.
            wifi_toggle_state(self.log, self.android_devices[0], False)
            if not initiate_call(self.log, ad_caller, callee_number):
                raise signals.TestFailure("Failed to initiate call")
            if not wait_and_answer_call(self.log, ad_callee, caller_number):
                raise signals.TestFailure("Answer call falied")
            if not self.is_phone_in_call_volte():
                raise signals.TestFailure("Phone call not via LTE")
            time.sleep(15)
            # Turn on the wifi and wait call to handover.
            wifi_toggle_state(self.log, self.android_devices[0], True)
            time.sleep(15)
            if not self._is_phone_in_call_iwlan():
                raise signals.TestFailure("LTE handover failed, call disconnected ")

            else:
                self.log.info("Handover Successful")

            if is_phone_in_call(self.log, ads[0]):
                # hangup call
                if not hangup_call(self.log, ads[0]):
                    raise signals.TestFailure("hangup_call fail.")

            else:
                raise signals.TestFailure("Unexpected call drop.")


        except Exception as e:
                self.log.error("Exception error %s", str(e))
                return False
        return True



""" Tests End """
