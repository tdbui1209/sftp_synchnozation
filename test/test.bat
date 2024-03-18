@echo off
@rem define variables
set "test_dir=test_sftp"
set "winscp_path="C:\Program Files (x86)\WinSCP\WinSCP.exe""
set "sync_script=..\script.txt"
set "setup_test_script=setup_test_script.txt"
set "remove_test_script=remove_test_script.txt"
set "test_1_script=test_1_script.txt"
set "test_3_script=test_3_script.txt"

@rem create test directory at local
mkdir %test_dir%
%winscp_path% /console /ini=nul /script=%setup_test_script%

@rem Test scenario 1
echo Hello > %test_dir%\test_1.txt
%winscp_path% /console /ini=nul /script=%test_1_script%
del %test_dir%\test_1.txt
%winscp_path% /console /ini=nul /script=%sync_script%
if exist %test_dir%\test_1.txt (
  echo Scenerio 1: PASS
) else (
  echo Scenerio 1: FAIL - File test_1.txt at local should be synchronized from ZEBRA server
)

@rem Test scenario 2
echo Hello > %test_dir%\test_2.txt
%winscp_path% /console /ini=nul /script=%sync_script%
if exist %test_dir%\test_2.txt (
  echo Scenerio 2: FAIL - File test_2.txt at local should be deleted as it is not present at ZEBRA server
) else (
  echo Scenerio 2: PASS
)

@rem Test scenario 3
echo HelloUSI > %test_dir%\test_3.txt
%winscp_path% /console /ini=nul /script=%test_3_script%
timeout 2 >nul
echo Hello > %test_dir%\test_3.txt
%winscp_path% /console /ini=nul /script=%sync_script%
>nul find "HelloUSI" %test_dir%\test_3.txt && (
  echo Scenerio 3: PASS
) || (
  echo Scenerio 3: FAIL - Content of file test_3.txt at local should be synchronized from ZEBRA server
)

@rem remove test directory at local
rmdir /s /q %test_dir%
@rem remove test directory at remote
%winscp_path% /console /ini=nul /script=%remove_test_script%

echo Test completed!
pause
