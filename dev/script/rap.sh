# !/bin/bash
set -exuo pipefail

# requires say and sox


SOUND_CLIPS_DIR="./sounds"
TMP_DIR="./tmp"

BPM=128
SONG=${SOUND_CLIPS_DIR}/shots_instruments_128_bpm_sampled.aiff

#BPM=60
#SONG=${SOUND_CLIPS_DIR}/smooth_jazz.aiff
#SONG=${SOUND_CLIPS_DIR}/shots_instruments_128_bpm_sampled.aiff


mkdir -p tmp

BEAT_LENGTH_SECONDS=`echo "60.0/${BPM}.0" | bc -l`

write_word() {
	say $1 -o ${TMP_DIR}/$1_tmp.aiff
	sox tmp/$1_tmp.aiff tmp/$1.aiff silence 1 0.1 1%
}


i=0
files=""
while IFS=, read -r word beats
do
	if [ "$word" = "REST" ]; then
		rest_length=`echo "$beats*${BEAT_LENGTH_SECONDS}" | bc -l`
		sox -n -r 22050 ${TMP_DIR}/${i}.aiff trim 0.0 $rest_length
	else
		echo $word
		say "$word" -o ${TMP_DIR}/${i}_tmp.aiff
		sox ${TMP_DIR}/${i}_tmp.aiff ${TMP_DIR}/${i}_trimmed.aiff silence 1 0.1 1%
		clip_length=`sox ${TMP_DIR}/${i}_trimmed.aiff -n stat 2>&1 | grep Length | awk '{print $3}'`
		scale_factor=`echo "${clip_length}/(${BEAT_LENGTH_SECONDS}*${beats})" | bc -l`
		sox ${TMP_DIR}/${i}_trimmed.aiff ${TMP_DIR}/${i}.aiff tempo $scale_factor
	fi
	files="${files} ${TMP_DIR}/${i}.aiff"
	i=$((i + 1))
done < "${1:-/dev/stdin}"

sox ${SOUND_CLIPS_DIR}/airhorn.aiff ${TMP_DIR}/airhorn_repeat.aiff repeat 10
sox ${SOUND_CLIPS_DIR}/yeah_what_ok.aiff ${TMP_DIR}/yeah_what_ok_repeat.aiff repeat 20
sox $files ${TMP_DIR}/speech.aiff repeat 10
#sox -m ${TMP_DIR}/speech.aiff $SONG ${TMP_DIR}/yeah_what_ok_repeat.aiff ${TMP_DIR}/mixed.aiff
sox -m ${TMP_DIR}/speech.aiff $SONG ${TMP_DIR}/mixed.aiff
play ${TMP_DIR}/mixed.aiff
