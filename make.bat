set project_name=example
set cmm_path=e:\sft\cmm_last\build
set asm_path=e:\sft\sjasmplus-1.18.2.win
set emulator_path=e:\sft\US0.39.0\unreal.exe
set zmakebas_path=e:\sft\zmakebas

python preprocessor.py %project_name%.c temp0.c
if not %errorlevel% == 0 pause && exit

%cmm_path%\cmm.exe temp0.asm temp0.c
if not %errorlevel% == 0 pause && exit

python optimizer.py temp0.asm temp1.asm
if not %errorlevel% == 0 pause && exit

python add_asm_options.py temp1.asm temp2.asm +bin +tap +hob org=#6000 project_name=%project_name% device=zxspectrum128
if not %errorlevel% == 0 pause && exit

%asm_path%\sjasmplus.exe --lst=%project_name%.lst --lstlab temp2.asm
if not %errorlevel% == 0 pause && exit

%zmakebas_path%\zmakebas.exe -a 10 -o boot.tap -n %project_name% %project_name%.bas

type boot.tap %project_name%_c.tap > %project_name%.tap
del %project_name%_c.tap

%emulator_path% %project_name%.tap && exit
pause
