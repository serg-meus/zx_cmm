project_name=example
start_address=32768
cmm_path=~/src/cmm_last/build
asm_path=~/src/sjasmplus
emul_path=~/src/unrealspeccyp
emul_file=unreal_speccy_portable
zmakebas_path=~/src/zmakebas

python preprocessor.py $project_name.c temp0.c
$cmm_path/cmm temp0.asm temp0.c
python optimizer.py temp0.asm temp1.asm
python add_asm_options.py temp1.asm temp2.asm +bin +tap org=$start_address project_name=$project_name device=zxspectrum128
$asm_path/sjasmplus --lst=$project_name.lst --lstlab temp2.asm
python replace_text.py $project_name.bas addr $start_address
$zmakebas_path/zmakebas -a 10 -o boot.tap -n $project_name $project_name.bas.tmp
cat boot.tap $project_name\_c.tap > $project_name.tap
rm $project_name\_c.tap boot.tap $project_name.bas.tmp
echo Size of binary in bytes:
stat -c %s $project_name.bin
cur_dir=$PWD
cd $emul_path
./$emul_file $cur_dir/$project_name.tap

