import colormap from 'colormap'

/**
 * 
 * @param {HTMLCanvasElement} canvas 
 * @param {String} cmap 
 */
function applyMap(canvas,cmap)
{
    const ctx = canvas.getContext('2d');
    const colormapData = colormap({
        colormap: cmap,
        nshades: 256,
        format: "rgba",
        alpha: 1,
      });

      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const data = imageData.data;
      for (let i = 0; i < data.length; i += 4) {

        const gray = data[i] * 0.299 + data[i + 1] * 0.587 + data[i + 2] * 0.114;
        const color = colormapData[Math.floor(gray)];

        data[i] = color[0];     
        data[i + 1] = color[1]; 
        data[i + 2] = color[2]; 
        // data[i + 3] = 255;      
      }

      ctx.putImageData(imageData, 0, 0);
}

export default applyMap