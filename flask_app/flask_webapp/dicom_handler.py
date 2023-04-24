from PIL import Image as pillow
import mudicom

def create_thumbnail(dcm_fn, output_fn, size, output_format=None):
    if not output_format:
        output_format = output_fn.split(".")[-1].upper()
    
    mu = mudicom.load(dcm_fn)
    mu.read()

    image = pillow.fromarray(mu.image.numpy.astype('uint8'))
    image.thumbnail(size)
    image.save(output_fn, output_format)