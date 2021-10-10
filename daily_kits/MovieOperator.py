#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Willie
# Created Date: 2021-10-10
# =============================================================================
"""
Extract audio from video with
`moviepy <https://zulko.github.io/moviepy/>`_

Install with conda `https://anaconda.org/conda-forge/moviepy`:
`conda install -c conda-forge moviepy`

"""

from moviepy.editor import *
import os


def convert_video_to_audio(video_file_path, audio_file_path):
    video_clip = VideoFileClip(video_file_path)
    audio_clip = video_clip.audio
    if audio_clip is None:
        print('video {} has no audio'.format(video_file_path))
        video_clip.close()
        return
    audio_clip.write_audiofile(audio_file_path)
    audio_clip.close()
    video_clip.close()


if __name__ == '__main__':
    print('Mission Start\n')
    count = 0
    root_dir = r'E:\media\baby'
    mp4_folder = root_dir + r'\super_simple_song_204_mp4'
    mp3_folder = root_dir + r'\super_simple_song_204_mp3'
    print('mp4_folder={}'.format(mp4_folder))
    print('mp3_folder={}'.format(mp3_folder))

    for video_file_name in os.listdir(mp4_folder):
        if video_file_name.endswith(".mp4"):
            video_file_full_path = mp4_folder + '\\' + video_file_name
            first_dot_index = video_file_name.index('.')
            str_fill_0 = video_file_name[0:first_dot_index].zfill(3)
            audio_file_full_path = mp3_folder + '\\' + str_fill_0 + '.' + video_file_name[first_dot_index + 1:]
            last_dot_index = audio_file_full_path.rfind('.')
            audio_file_full_path = audio_file_full_path[0:last_dot_index] + '.mp3'

            if not os.path.exists(audio_file_full_path):
                print('No.{} start convert {} to {}'.format(count, video_file_full_path, audio_file_full_path))
                convert_video_to_audio(video_file_full_path, audio_file_full_path)
            else:
                print('No.{} no need to convert {}'.format(count, audio_file_full_path))
                count = count + 1
    print('Mission complete total mp3 number={}'.format(count))
