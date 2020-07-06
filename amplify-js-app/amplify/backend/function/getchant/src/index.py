import boto3
import hashlib
import sox

BUCKET = 'partyjams-songs'
BACKING_TRACK_FOLDER = 'backing_tracks'

TMP_DIR = '/tmp'
BACKING_TRACKS = {
    "shots": {
        "bpm": 128,
        "file": "shots_instruments_128_bpm.mp3"
    }
}


def handler(event, context):
    polly = boto3.client('polly')
    s3 = boto3.client('s3')

    lyrics = getchant_lyrics(event['word'])
    song = "shots"
    bpm = BACKING_TRACKS[song]['bpm']
    beat_length_seconds = bpm / 60
    song_file = BACKING_TRACKS[song]['file']

    local_files = []
    for lyric in lyrics:
        phrase = lyric['phrase']
        hex_digest = hashlib.md5(bytes(phrase, 'utf-8')).hexdigest()
        local_file = TMP_DIR + '/' + hex_digest + '.mp3'

        # First, write basic response to local
        response = polly.synthesize_speech(
            VoiceId='Joanna', OutputFormat='mp3', Text=phrase)
        with open(local_file, 'wb') as fout:
            fout.write(response['AudioStream'].read())

        # Figure out desired length of clip
        clip_length = sox.file_info.duration(local_file)
        scale_factor = clip_length / (beat_length_seconds * lyric['beats'])

        # Resize clip and write
        transformer = sox.Transformer()
        transformer.tempo(scale_factor)

        local_file_scaled = TMP_DIR + '/' + hex_digest + 'scaled' + '.mp3'
        transformer.build(local_file, local_file_scaled)
        local_files.append(local_file_scaled)

    cbn = sox.Combiner()
    cbn.convert(n_channels=1)
    cbn.build(local_files, TMP_DIR + '/lyrics.mp3', 'concatenate')
    s3.download_file(BUCKET, BACKING_TRACK_FOLDER + '/' +
                     song_file, TMP_DIR + '/' + song_file)

    backing_cbn = sox.Combiner()
    backing_cbn.convert(n_channels=1)
    backing_cbn.build([TMP_DIR + '/lyrics.mp3', TMP_DIR +
                       '/' + song_file], TMP_DIR + '/final.mp3', 'merge')

    s3.upload_file(TMP_DIR + '/final.mp3', BUCKET, 'final.mp3')

    return {
        "url": "s3://" + BUCKET + "/final.mp3",
        "lyrics": [{"phrase": l['phrase'], "seconds": l['beats'] * beat_length_seconds} for l in lyrics]
    }


def getchant_lyrics(word):
    beats = [1, 1, 1/3, 1/3, 1/3]*4
    return [{"phrase": word, "beats": b} for b in beats]
