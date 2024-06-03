#!/bin/bash

for data in TelLiveEmergencyTest TelLiveGFTDSDSDDSSwitchTest TelLiveGFTDSDSMessageTest TelLiveGFTDSDSSupplementaryServiceTest TelLiveGFTDSDSVoiceTest TelLiveGFTDSDSWfcSupplementaryServiceTest TelLiveGFTRcsTest TelLiveImsSettingsTest TelLiveLockedSimTest TelLiveMobilityStressTest TelLiveNoQXDMLogTest TelLiveNoSimTest TelLivePostflightTest TelLivePreflightTest TelLiveProjectFiTest TelLiveRcsTest TelLiveRebootStressTest TelLiveRilCstVoiceTest TelLiveRilDataKpiTest TelLiveRilImsKpiTest TelLiveRilImsKpiTest TelLiveRilMessageKpiTest TelLiveSettingsTest TelLiveSmokeTest TelLiveSmsTest TelLiveStressCallTest TelLiveStressDataTest TelLiveStressFdrTest TelLiveStressSmsTest TelLiveStressTest TelLiveVideoDataTest TelLiveVideoTest TelLiveVoiceConfTest TelLiveVoiceTest TelWifiDataTest TelWifiVideoTest TelWifiVoiceTest
do
  echo $data
  touch $data.md
  echo "::: tests.google.tel.live.$data" >$data.md
done