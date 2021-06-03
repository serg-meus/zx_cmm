set project_name=example
set cmm_path=e:\sft\cmm_last\build
set asm_path=e:\sft\sjasmplus-1.18.2.win
set unreal_path=e:\sft\US0.39.0

python preprocessor.py %project_name%.c temp0.c
if not %errorlevel% == 0 pause && exit

%cmm_path%\cmm.exe temp0.asm temp0.c
if not %errorlevel% == 0 pause && exit

python optimizer.py temp0.asm temp1.asm
if not %errorlevel% == 0 pause && exit

python add_asm_options.py temp1.asm %project_name%.asm +bin +tap +hob org=#6000 project_name=%project_name% device=zxspectrum48
if not %errorlevel% == 0 pause && exit

%asm_path%\sjasmplus.exe --lst=%project_name%.lst --lstlab %project_name%.asm
if not %errorlevel% == 0 pause && exit

type boot.tap %project_name%_c.tap > %project_name%.tap
del %project_name%_c.tap

python change_prog_name_in_tap.py %project_name%.tap %project_name%

%unreal_path%\unreal.exe %project_name%.tap && exit
pause
