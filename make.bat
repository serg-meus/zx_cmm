set project_name=example
set start_address=32768
set cmm_path=c:\my\sft\cmm_last\build
set asm_path=c:\my\sft\sjasmplus
set emulator_path=c:\my\sft\US0390\unreal.exe
set zmakebas_path=c:\my\sft\zmakebas

python preprocessor.py %project_name%.c temp0.c
if not %errorlevel% == 0 pause && exit

%cmm_path%\cmm.exe temp0.asm temp0.c
if not %errorlevel% == 0 pause && exit

python optimizer.py temp0.asm temp1.asm
if not %errorlevel% == 0 pause && exit

python add_asm_options.py temp1.asm temp2.asm +bin +tap ^
	org=%start_address% project_name=%project_name% device=zxspectrum48
if not %errorlevel% == 0 pause && exit

%asm_path%\sjasmplus.exe --lst=%project_name%.lst --lstlab temp2.asm
if not %errorlevel% == 0 pause && exit

python replace_text.py %project_name%.bas addr %start_address%
%zmakebas_path%\zmakebas.exe -a 10 -o boot.tap -n %project_name% ^
	%project_name%.bas.tmp

type boot.tap %project_name%_c.tap > %project_name%.tap
del %project_name%_c.tap %project_name%.bas.tmp boot.tap

echo off
echo Size of binary in bytes:
for %%I in (%project_name%.bin) do @echo %%~zI

%emulator_path% %project_name%.tap && exit
pause
