from os import listdir

import pdal
import json
from pipeline_wrapper import PipelineWrapper


class Tile:
    def __init__(self, cloud, bounds, pipeline, output, buffer=None, remove_buffer=None, name=None):
        self.cloud = cloud
        self.bounds = bounds
        self.name = name if name else str(int(self.bounds.min_x)) + '_' + str(int(self.bounds.min_y))
        self.pipeline_wrapper = PipelineWrapper(pipeline)
        self.output = output
        self.buffer = buffer if buffer else None
        self.remove_buffer = remove_buffer if remove_buffer else None

    def add_buffer(self):
        self.bounds.min_x -= self.buffer[0]
        self.bounds.min_y -= self.buffer[1]
        self.bounds.max_x += self.buffer[0]
        self.bounds.max_y += self.buffer[1]

    def remove_buffer(self):
        self.bounds.min_x += self.buffer[0]
        self.bounds.min_y += self.buffer[1]
        self.bounds.max_x -= self.buffer[0]
        self.bounds.max_y -= self.buffer[1]

    def link_pipeline(self, is_single_file) -> pdal.Pipeline:
        writers = self.pipeline_wrapper.get_writers()

        try:
            compression = writers[0]["compression"]
            extension = '.laz' if compression == 'laszip' or compression == 'lazperf' else '.las'
        except KeyError:
            extension = '.' + writers[0]["type"].split(".")[1] + ".las" if writers[0]["type"].split(".")[1] == "copc" \
                else "." + writers[0]["type"].split(".")[1]

        if is_single_file:
            if self.buffer:
                self.add_buffer()
                if self.remove_buffer:
                    self.remove_buffer()

            self.pipeline_wrapper.add_crop_filter(self.bounds)

        self.pipeline_wrapper.set_readers_filename(self.cloud.filepath)
        self.pipeline_wrapper.set_writers_filename(self.output + "/" + self.name + extension)

        return pdal.Pipeline(json.dumps(self.pipeline_wrapper.loaded_pipeline))

    def __str__(self):
        return f'{self.name} - {self.bounds}'
