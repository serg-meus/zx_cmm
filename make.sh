project_name=example
cmm_path=~/src/cmm_last/build
asm_path=~/src/sjasmplus
unreal_path=~/src/unrealspeccyp

python preprocessor.py $project_name.c temp0.c
$cmm_path/cmm temp0.asm temp0.c
python optimizer.py temp0.asm temp1.asm
python add_asm_options.py temp1.asm $project_name.asm +bin +tap +hob org=#6000 project_name=$project_name device=zxspectrum48
python optimizer.py temp0.asm temp1.asm
$asm_path/sjasmplus --lst=example.lst --lstlab example.asm
cur_dir=$PWD
cd $unreal_path
./unreal_speccy_portable $cur_dir/$project_name.tap

