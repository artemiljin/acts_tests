# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: bluetooth.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0f\x62luetooth.proto\x12\'bluetooth.metrics.BluetoothMetricsProto\"\x8a\x05\n\x0c\x42luetoothLog\x12J\n\x07session\x18\x01 \x03(\x0b\x32\x39.bluetooth.metrics.BluetoothMetricsProto.BluetoothSession\x12\x46\n\npair_event\x18\x02 \x03(\x0b\x32\x32.bluetooth.metrics.BluetoothMetricsProto.PairEvent\x12\x46\n\nwake_event\x18\x03 \x03(\x0b\x32\x32.bluetooth.metrics.BluetoothMetricsProto.WakeEvent\x12\x46\n\nscan_event\x18\x04 \x03(\x0b\x32\x32.bluetooth.metrics.BluetoothMetricsProto.ScanEvent\x12\x1a\n\x12num_bonded_devices\x18\x05 \x01(\x05\x12\x1d\n\x15num_bluetooth_session\x18\x06 \x01(\x03\x12\x16\n\x0enum_pair_event\x18\x07 \x01(\x03\x12\x16\n\x0enum_wake_event\x18\x08 \x01(\x03\x12\x16\n\x0enum_scan_event\x18\t \x01(\x03\x12\x61\n\x18profile_connection_stats\x18\n \x03(\x0b\x32?.bluetooth.metrics.BluetoothMetricsProto.ProfileConnectionStats\x12p\n headset_profile_connection_stats\x18\x0b \x03(\x0b\x32\x46.bluetooth.metrics.BluetoothMetricsProto.HeadsetProfileConnectionStats\"\xdf\x01\n\nDeviceInfo\x12\x14\n\x0c\x64\x65vice_class\x18\x01 \x01(\x05\x12S\n\x0b\x64\x65vice_type\x18\x02 \x01(\x0e\x32>.bluetooth.metrics.BluetoothMetricsProto.DeviceInfo.DeviceType\"f\n\nDeviceType\x12\x17\n\x13\x44\x45VICE_TYPE_UNKNOWN\x10\x00\x12\x15\n\x11\x44\x45VICE_TYPE_BREDR\x10\x01\x12\x12\n\x0e\x44\x45VICE_TYPE_LE\x10\x02\x12\x14\n\x10\x44\x45VICE_TYPE_DUMO\x10\x03\"\x8f\x06\n\x10\x42luetoothSession\x12\x1c\n\x14session_duration_sec\x18\x02 \x01(\x03\x12v\n\x1a\x63onnection_technology_type\x18\x03 \x01(\x0e\x32R.bluetooth.metrics.BluetoothMetricsProto.BluetoothSession.ConnectionTechnologyType\x12\x1d\n\x11\x64isconnect_reason\x18\x04 \x01(\tB\x02\x18\x01\x12P\n\x13\x64\x65vice_connected_to\x18\x05 \x01(\x0b\x32\x33.bluetooth.metrics.BluetoothMetricsProto.DeviceInfo\x12N\n\x0erfcomm_session\x18\x06 \x01(\x0b\x32\x36.bluetooth.metrics.BluetoothMetricsProto.RFCommSession\x12J\n\x0c\x61\x32\x64p_session\x18\x07 \x01(\x0b\x32\x34.bluetooth.metrics.BluetoothMetricsProto.A2DPSession\x12n\n\x16\x64isconnect_reason_type\x18\x08 \x01(\x0e\x32N.bluetooth.metrics.BluetoothMetricsProto.BluetoothSession.DisconnectReasonType\"\x8b\x01\n\x18\x43onnectionTechnologyType\x12&\n\"CONNECTION_TECHNOLOGY_TYPE_UNKNOWN\x10\x00\x12!\n\x1d\x43ONNECTION_TECHNOLOGY_TYPE_LE\x10\x01\x12$\n CONNECTION_TECHNOLOGY_TYPE_BREDR\x10\x02\"Z\n\x14\x44isconnectReasonType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x10\n\x0cMETRICS_DUMP\x10\x01\x12#\n\x1fNEXT_START_WITHOUT_END_PREVIOUS\x10\x02\"3\n\rRFCommSession\x12\x10\n\x08rx_bytes\x18\x01 \x01(\x05\x12\x10\n\x08tx_bytes\x18\x02 \x01(\x05\"\xf9\x02\n\x0b\x41\x32\x44PSession\x12\x1e\n\x16media_timer_min_millis\x18\x01 \x01(\x05\x12\x1e\n\x16media_timer_max_millis\x18\x02 \x01(\x05\x12\x1e\n\x16media_timer_avg_millis\x18\x03 \x01(\x05\x12!\n\x19\x62uffer_overruns_max_count\x18\x04 \x01(\x05\x12\x1d\n\x15\x62uffer_overruns_total\x18\x05 \x01(\x05\x12 \n\x18\x62uffer_underruns_average\x18\x06 \x01(\x02\x12\x1e\n\x16\x62uffer_underruns_count\x18\x07 \x01(\x05\x12\x1d\n\x15\x61udio_duration_millis\x18\x08 \x01(\x03\x12N\n\x0csource_codec\x18\t \x01(\x0e\x32\x38.bluetooth.metrics.BluetoothMetricsProto.A2dpSourceCodec\x12\x17\n\x0fis_a2dp_offload\x18\n \x01(\x08\"\x92\x01\n\tPairEvent\x12\x19\n\x11\x64isconnect_reason\x18\x01 \x01(\x05\x12\x19\n\x11\x65vent_time_millis\x18\x02 \x01(\x03\x12O\n\x12\x64\x65vice_paired_with\x18\x03 \x01(\x0b\x32\x33.bluetooth.metrics.BluetoothMetricsProto.DeviceInfo\"\xdc\x01\n\tWakeEvent\x12Y\n\x0fwake_event_type\x18\x01 \x01(\x0e\x32@.bluetooth.metrics.BluetoothMetricsProto.WakeEvent.WakeEventType\x12\x11\n\trequestor\x18\x02 \x01(\t\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\x19\n\x11\x65vent_time_millis\x18\x04 \x01(\x03\"8\n\rWakeEventType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x0c\n\x08\x41\x43QUIRED\x10\x01\x12\x0c\n\x08RELEASED\x10\x02\"\xc4\x03\n\tScanEvent\x12Y\n\x0fscan_event_type\x18\x01 \x01(\x0e\x32@.bluetooth.metrics.BluetoothMetricsProto.ScanEvent.ScanEventType\x12\x11\n\tinitiator\x18\x02 \x01(\t\x12\x63\n\x14scan_technology_type\x18\x03 \x01(\x0e\x32\x45.bluetooth.metrics.BluetoothMetricsProto.ScanEvent.ScanTechnologyType\x12\x16\n\x0enumber_results\x18\x04 \x01(\x05\x12\x19\n\x11\x65vent_time_millis\x18\x05 \x01(\x03\"u\n\x12ScanTechnologyType\x12\x15\n\x11SCAN_TYPE_UNKNOWN\x10\x00\x12\x15\n\x11SCAN_TECH_TYPE_LE\x10\x01\x12\x18\n\x14SCAN_TECH_TYPE_BREDR\x10\x02\x12\x17\n\x13SCAN_TECH_TYPE_BOTH\x10\x03\":\n\rScanEventType\x12\x14\n\x10SCAN_EVENT_START\x10\x00\x12\x13\n\x0fSCAN_EVENT_STOP\x10\x01\"}\n\x16ProfileConnectionStats\x12\x46\n\nprofile_id\x18\x01 \x01(\x0e\x32\x32.bluetooth.metrics.BluetoothMetricsProto.ProfileId\x12\x1b\n\x13num_times_connected\x18\x02 \x01(\x05\"\x97\x01\n\x1dHeadsetProfileConnectionStats\x12Y\n\x14headset_profile_type\x18\x01 \x01(\x0e\x32;.bluetooth.metrics.BluetoothMetricsProto.HeadsetProfileType\x12\x1b\n\x13num_times_connected\x18\x02 \x01(\x05*\xbd\x01\n\x0f\x41\x32\x64pSourceCodec\x12\x1d\n\x19\x41\x32\x44P_SOURCE_CODEC_UNKNOWN\x10\x00\x12\x19\n\x15\x41\x32\x44P_SOURCE_CODEC_SBC\x10\x01\x12\x19\n\x15\x41\x32\x44P_SOURCE_CODEC_AAC\x10\x02\x12\x1a\n\x16\x41\x32\x44P_SOURCE_CODEC_APTX\x10\x03\x12\x1d\n\x19\x41\x32\x44P_SOURCE_CODEC_APTX_HD\x10\x04\x12\x1a\n\x16\x41\x32\x44P_SOURCE_CODEC_LDAC\x10\x05*\xa0\x02\n\tProfileId\x12\x13\n\x0fPROFILE_UNKNOWN\x10\x00\x12\x0b\n\x07HEADSET\x10\x01\x12\x08\n\x04\x41\x32\x44P\x10\x02\x12\n\n\x06HEALTH\x10\x03\x12\x0c\n\x08HID_HOST\x10\x04\x12\x07\n\x03PAN\x10\x05\x12\x08\n\x04PBAP\x10\x06\x12\x08\n\x04GATT\x10\x07\x12\x0f\n\x0bGATT_SERVER\x10\x08\x12\x07\n\x03MAP\x10\t\x12\x07\n\x03SAP\x10\n\x12\r\n\tA2DP_SINK\x10\x0b\x12\x14\n\x10\x41VRCP_CONTROLLER\x10\x0c\x12\t\n\x05\x41VRCP\x10\r\x12\x12\n\x0eHEADSET_CLIENT\x10\x10\x12\x0f\n\x0bPBAP_CLIENT\x10\x11\x12\x0e\n\nMAP_CLIENT\x10\x12\x12\x0e\n\nHID_DEVICE\x10\x13\x12\x07\n\x03OPP\x10\x14\x12\x0f\n\x0bHEARING_AID\x10\x15*C\n\x12HeadsetProfileType\x12\x1b\n\x17HEADSET_PROFILE_UNKNOWN\x10\x00\x12\x07\n\x03HSP\x10\x01\x12\x07\n\x03HFP\x10\x02\x42\x30\n\x15\x63om.android.bluetoothB\x15\x42luetoothMetricsProtoH\x03')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'bluetooth_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\025com.android.bluetoothB\025BluetoothMetricsProtoH\003'
  _BLUETOOTHSESSION.fields_by_name['disconnect_reason']._options = None
  _BLUETOOTHSESSION.fields_by_name['disconnect_reason']._serialized_options = b'\030\001'
  _A2DPSOURCECODEC._serialized_start=3267
  _A2DPSOURCECODEC._serialized_end=3456
  _PROFILEID._serialized_start=3459
  _PROFILEID._serialized_end=3747
  _HEADSETPROFILETYPE._serialized_start=3749
  _HEADSETPROFILETYPE._serialized_end=3816
  _BLUETOOTHLOG._serialized_start=61
  _BLUETOOTHLOG._serialized_end=711
  _DEVICEINFO._serialized_start=714
  _DEVICEINFO._serialized_end=937
  _DEVICEINFO_DEVICETYPE._serialized_start=835
  _DEVICEINFO_DEVICETYPE._serialized_end=937
  _BLUETOOTHSESSION._serialized_start=940
  _BLUETOOTHSESSION._serialized_end=1723
  _BLUETOOTHSESSION_CONNECTIONTECHNOLOGYTYPE._serialized_start=1492
  _BLUETOOTHSESSION_CONNECTIONTECHNOLOGYTYPE._serialized_end=1631
  _BLUETOOTHSESSION_DISCONNECTREASONTYPE._serialized_start=1633
  _BLUETOOTHSESSION_DISCONNECTREASONTYPE._serialized_end=1723
  _RFCOMMSESSION._serialized_start=1725
  _RFCOMMSESSION._serialized_end=1776
  _A2DPSESSION._serialized_start=1779
  _A2DPSESSION._serialized_end=2156
  _PAIREVENT._serialized_start=2159
  _PAIREVENT._serialized_end=2305
  _WAKEEVENT._serialized_start=2308
  _WAKEEVENT._serialized_end=2528
  _WAKEEVENT_WAKEEVENTTYPE._serialized_start=2472
  _WAKEEVENT_WAKEEVENTTYPE._serialized_end=2528
  _SCANEVENT._serialized_start=2531
  _SCANEVENT._serialized_end=2983
  _SCANEVENT_SCANTECHNOLOGYTYPE._serialized_start=2806
  _SCANEVENT_SCANTECHNOLOGYTYPE._serialized_end=2923
  _SCANEVENT_SCANEVENTTYPE._serialized_start=2925
  _SCANEVENT_SCANEVENTTYPE._serialized_end=2983
  _PROFILECONNECTIONSTATS._serialized_start=2985
  _PROFILECONNECTIONSTATS._serialized_end=3110
  _HEADSETPROFILECONNECTIONSTATS._serialized_start=3113
  _HEADSETPROFILECONNECTIONSTATS._serialized_end=3264
# @@protoc_insertion_point(module_scope)
