/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const createSong = /* GraphQL */ `
  mutation CreateSong(
    $name: String
    $backing_track: BackingTrack
    $input_lyric: [Lyric]
  ) {
    createSong(
      name: $name
      backing_track: $backing_track
      input_lyric: $input_lyric
    ) {
      hash
      name
      lyrics {
        phrase
        seconds_length
      }
    }
  }
`;
