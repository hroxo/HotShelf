# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    snip.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: hroxo <hroxo@student.42porto.com>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/11/12 11:09:21 by hroxo             #+#    #+#              #
#    Updated: 2025/11/12 11:10:53 by hroxo            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import io, math
from typing import Dict, List, Tuple
from PIL import Image

def warp_quad_to_bytes(pil_img: Image.Image, quad: Dict, mime="image/jpeg", quality=92, scale=1.0) -> bytes:
    """
    quad: {'top_left':[x,y], 'top_right':[x,y], 'bottom_right':[x,y], 'bottom_left':[x,y]}
    Faz warp do quadrilátero para um retângulo estimando W/H pelos lados.
    """
    QUAD    = getattr(getattr(Image, "Transform", Image), "QUAD", getattr(Image, "QUAD"))
    BICUBIC = getattr(Image, "BICUBIC", 3)

    tl = tuple(quad["top_left"]);     tr = tuple(quad["top_right"])
    br = tuple(quad["bottom_right"]); bl = tuple(quad["bottom_left"])

    def dist(a, b): return math.hypot(a[0]-b[0], a[1]-b[1])
    width  = int(round(scale * (dist(tl, tr) + dist(bl, br)) / 2.0))
    height = int(round(scale * (dist(tl, bl) + dist(tr, br)) / 2.0))
    width  = max(8, width); height = max(8, height)

    quad_src = (tl[0], tl[1],  bl[0], bl[1],  br[0], br[1],  tr[0], tr[1])
    warped = pil_img.transform((width, height), QUAD, data=quad_src, resample=BICUBIC)

    buf = io.BytesIO()
    if mime == "image/png":
        warped.save(buf, format="PNG")
    else:
        warped.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()

