# -*- coding: utf-8 -*-
import time
import concurrent.futures

from tatneft_ai.audio2text.voice_detection import whisper_audio2text
from tatneft_ai.utils_hack_tatneft.diarization import PersonAssociator
from tatneft_ai.utils_hack_tatneft.image_works.person_matching import VideoProcessor
from tatneft_ai.utils_hack_tatneft.mathcing_persons import AudioTextMerger


class MFiLkO:
    async def __init__(self, path_video, path_audio):
        self.path_video = path_video
        self.path_audio = path_audio

    async def run(self, sync_mode=True):
        photo = None
        if sync_mode:
            # cv routine
            # will  be in next version
            print("video process")
            video_processor = VideoProcessor(
                self.path_video,
                f"tatneft_ai/source/output_video/{str(time.time())}.mp4"
            )
            photo = video_processor.process_video()
            # voice routine
            print("start video))")
            start_time = time.time()
            persons_subt = PersonAssociator().associate_persons(self.path_audio)
            end_time = time.time()
            print(f"finished subt time = {end_time - start_time}")

            start_time = time.time()
            dialogs = whisper_audio2text(self.path_audio)
            end_time = time.time()
            print(f"finish whisper = {end_time - start_time}")

            replics = await self._merge(dialogs, persons_subt)

            return await self._made_persons(replics, photo)
        else:
            start_time = time.time()

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_persons = executor.submit(await run_associate_persons, self.path_audio)
                print("start persons")
                future_dialogs = executor.submit(await run_whisper, self.path_audio)
                print("start whisper")

                persons_subt = future_persons.result()
                dialogs = future_dialogs.result()

            end_time = time.time()
            print(f"finish parallel = {end_time - start_time}")
            replics = await self._merge(dialogs, persons_subt)

            return await self._made_persons(replics, photo)

    async def _made_persons(self, replics, photos):
        merger = AudioTextMerger(
            replics,
            photos,
        )
        updated_transcription = merger.update_transcription_with_photos()

        return updated_transcription

    async def _merge(self, dialogs, persons):
        # print(dialogs)
        # print(persons)
        final_annotations = []
        for segment, _, speaker in persons.itertracks(yield_label=True):
            for i, item in enumerate(dialogs):
                if segment.start <= item["start"] < segment.end:
                    text = item["text"]
                    start = item["start"]
                    end = item["end"]
                    final_annotations.append({
                        "speaker": speaker,
                        "start": start,
                        "end": end,
                        "text": text,
                        "photo": None,
                    })
                    # final_annotations.append(f'(спикер_{speaker})[{start:.2f} - {end:.2f}] {text}')
        return final_annotations


async def run_associate_persons(path_audio):
    return PersonAssociator().associate_persons(path_audio)


async def run_whisper(path_audio):
    return whisper_audio2text(path_audio)