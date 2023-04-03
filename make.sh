project_name=example
cmm_path=~/src/cmm_last/build
asm_path=~/src/sjasmplus
emul_path=~/src/unrealspeccyp
emul_file=unreal_speccy_portable
zmakebas_path=~/src/zmakebas

python preprocessor.py $project_name.c temp0.c
$cmm_path/cmm temp0.asm temp0.c
python optimizer.py temp0.asm temp1.asm
python add_asm_options.py temp1.asm temp2.asm +bin +tap +hob org=#6000 project_name=$project_name device=zxspectrum128
$asm_path/sjasmplus --lst=$project_name.lst --lstlab temp2.asm
$zmakebas_path/zmakebas -a 10 -o boot.tap -n $project_name $project_name.bas
cat boot.tap $project_name\_c.tap > $project_name.tap
#rm $project_name\_c.tap
cur_dir=$PWD
cd $emul_path
./$emul_file $cur_dir/$project_name.tap

