import boto3
import hashlib
import sox
import os
import hashlib
import pprint
from time import time

BUCKET = 'partyjams-songs83029-' + os.environ.get('ENV')
BACKING_TRACK_FOLDER = 'backing_tracks'

TMP_DIR = '/tmp'
BACKING_TRACKS = {
    "shots": {
        "bpm": 128,
        "file": "shots_instruments_128_bpm.mp3"
    }
}

def handler(event, context):
    start_time = time()
    polly = boto3.client('polly')
    s3 = boto3.client('s3')

    lyrics = getchant_lyrics(event['word'])
    song = "shots"
    bpm = BACKING_TRACKS[song]['bpm']
    seconds_per_beat = 60 / bpm
    song_file = BACKING_TRACKS[song]['file']

    # TODO: skip all of this if the s3 object already exists

    local_files = []
    print('writing phrase files')
    print(time() - start_time)
    for lyric in lyrics:
        hex_digest = hashlib.md5(bytes(pprint.pformat(lyric), 'utf-8')).hexdigest()
        phrase = lyric['phrase']
        local_file = TMP_DIR + '/' + hex_digest + '.mp3'
        local_file_trimmed = TMP_DIR + '/' + hex_digest + '-trimmed.mp3'
        local_file_scaled = TMP_DIR + '/' + hex_digest + '-scaled.mp3'
        if not os.path.exists(local_file_scaled): # The same phrase might exists more than once
            # First, write basic response to local
            response = polly.synthesize_speech(
                VoiceId='Joanna', OutputFormat='mp3', Text=phrase)
            with open(local_file, 'wb') as fout:
                fout.write(response['AudioStream'].read())

            # Trim silence
            transformer = sox.Transformer()
            transformer.silence(1, 0.1,0.01)
            transformer.build(local_file, local_file_trimmed)

            # Figure out desired length of clip            
            clip_length = sox.file_info.duration(local_file_trimmed)
            print('clip_length = ' + str(clip_length))
            scale_factor = clip_length / (seconds_per_beat * lyric['beats'])
            print('scale factor for word: ' + phrase + ' = ' + str(scale_factor))

            # Resize clip and write
            transformer = sox.Transformer()
            transformer.tempo(scale_factor)
            transformer.build(local_file_trimmed, local_file_scaled)
            # This is wrong somehow. Unsure if it is silence or some kind of problem with the splicing together
            print("clip length scaled = " + str(sox.file_info.duration(local_file_scaled)))
        local_files.append(local_file_scaled)

    print('concatenating lyric files')
    print(time() - start_time)
    cbn = sox.Combiner()
    cbn.convert(n_channels=1)
    cbn.build(local_files, TMP_DIR + '/lyrics.mp3', 'concatenate')


    print('downloading backing track')
    print(time() - start_time)
    s3.download_file(BUCKET, BACKING_TRACK_FOLDER + '/' +
                     song_file, TMP_DIR + '/' + song_file)

    backing_cbn = sox.Combiner()
    backing_cbn.convert(n_channels=1)

    print('combining lyric and backing tracks')
    print(time() - start_time)
    final_filename = str(round(time())) + "-final.mp3"
    backing_cbn.build([TMP_DIR + '/lyrics.mp3', TMP_DIR +
                       '/' + song_file], TMP_DIR + '/' + final_filename, 'merge')


    print('uploading track')
    print(time() - start_time)
    s3.upload_file(TMP_DIR + '/' + final_filename, BUCKET, final_filename)

    return {
        "url": "s3://" + BUCKET + "/" + final_filename,
        "lyrics": [{"phrase": l['phrase'], "seconds": l['beats'] * seconds_per_beat} for l in lyrics]
    }


def getchant_lyrics(word):
    beats = [1, 1, 2/3, 2/3, 2/3]*4
    return [{"phrase": word, "beats": b} for b in beats]
