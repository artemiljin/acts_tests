# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: telephony_metric.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16telephony_metric.proto\x12\x33wireless.android.platform.testing.telephony.metrics\"\xf6\x04\n\x18TelephonyVoiceTestResult\x12h\n\x06result\x18\x01 \x01(\x0e\x32X.wireless.android.platform.testing.telephony.metrics.TelephonyVoiceTestResult.CallResult\x12\x1f\n\x17\x63\x61ll_setup_time_latency\x18\x02 \x01(\x02\"\xce\x03\n\nCallResult\x12%\n\x18UNAVAILABLE_NETWORK_TYPE\x10\xfe\xff\xff\xff\xff\xff\xff\xff\xff\x01\x12\x1f\n\x12\x43\x41LL_SETUP_FAILURE\x10\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01\x12\x0b\n\x07SUCCESS\x10\x00\x12\x13\n\x0fINITIATE_FAILED\x10\x01\x12\"\n\x1eNO_RING_EVENT_OR_ANSWER_FAILED\x10\x02\x12\x14\n\x10NO_CALL_ID_FOUND\x10\x03\x12.\n*CALL_STATE_NOT_ACTIVE_DURING_ESTABLISHMENT\x10\x04\x12/\n+AUDIO_STATE_NOT_INCALL_DURING_ESTABLISHMENT\x10\x05\x12*\n&AUDIO_STATE_NOT_INCALL_AFTER_CONNECTED\x10\x06\x12\x31\n-CALL_DROP_OR_WRONG_STATE_DURING_ESTABLISHMENT\x10\x07\x12,\n(CALL_DROP_OR_WRONG_STATE_AFTER_CONNECTED\x10\x08\x12\x14\n\x10\x43\x41LL_HANGUP_FAIL\x10\t\x12\x18\n\x14\x43\x41LL_ID_CLEANUP_FAIL\x10\n\"|\n\x1aTelephonyVoiceStressResult\x12^\n\x07results\x18\x01 \x03(\x0b\x32M.wireless.android.platform.testing.telephony.metrics.TelephonyVoiceTestResult')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'telephony_metric_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _TELEPHONYVOICETESTRESULT._serialized_start=80
  _TELEPHONYVOICETESTRESULT._serialized_end=710
  _TELEPHONYVOICETESTRESULT_CALLRESULT._serialized_start=248
  _TELEPHONYVOICETESTRESULT_CALLRESULT._serialized_end=710
  _TELEPHONYVOICESTRESSRESULT._serialized_start=712
  _TELEPHONYVOICESTRESSRESULT._serialized_end=836
# @@protoc_insertion_point(module_scope)
