from ...renderable import Renderable
from ...renderable.heading import Heading
from ...renderable.toc import ToC
from .. import Processor


class TocPreProcessor(Processor):
    def process(self, renderables: list[Renderable]):
        renderables_iter = iter(renderables)

        toc = None
        for renderable in renderables_iter:
            if isinstance(renderable, ToC):
                toc = renderable
                break

        if toc:
            for renderable in renderables_iter:
                if isinstance(renderable, Heading):
                    toc.add_item(renderable.level, renderable.text, renderable.is_numbered,
                                 renderable.anchor)


class TocPostProcessor(Processor):
    def __init__(self, pages_offset: int = 0):
        self._pages_offset = pages_offset

    def process(self, renderables: list[Renderable]):
        renderables_iter = iter(renderables)

        toc = None
        for renderable in renderables_iter:
            if isinstance(renderable, ToC):
                toc = renderable
                break

        if toc:
            i = 0
            for renderable in renderables_iter:
                if isinstance(renderable, Heading):
                    toc.set_page(i, renderable.rendered_page + self._pages_offset)
                    i += 1
