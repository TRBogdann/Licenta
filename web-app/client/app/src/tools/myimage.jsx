import { getElement } from "dropzone";

export function blendPixels(fg, bg) {
    
    const [r1, g1, b1, a1] = [fg[0]/255.,fg[1]/255.,fg[2]/255.,fg[3]/255.] 
    const [r2, g2, b2, a2] = [bg[0]/255.,bg[1]/255.,bg[2]/255.,bg[3]/255.]
    
    const outA = a1 + a2 * (1 - a1);
    let outR = 0, outG = 0, outB = 0;
    if (outA > 0) {
      outR = (r1 * a1 + r2 * a2 * (1 - a1)) / outA;
      outG = (g1 * a1 + g2 * a2 * (1 - a1)) / outA;
      outB = (b1 * a1 + b2 * a2 * (1 - a1)) / outA;
    }
  
    return [
      Math.round(outR * 255),
      Math.round(outG * 255),
      Math.round(outB * 255),
      Math.round(outA * 255)
    ];
  }

export function blendAndSave(canvas1,canvas2) {
    const width = canvas1.width;
    const height = canvas1.height;
  
    const ctx1 = canvas1.getContext('2d');
    const ctx2 = canvas2.getContext('2d');
  
    const imgData1 = ctx1.getImageData(0, 0, width, height);
    const imgData2 = ctx2.getImageData(0, 0, width, height);
  
    const blendedCanvas = document.createElement('canvas');
    blendedCanvas.width = width;
    blendedCanvas.height = height;
    const blendedCtx = blendedCanvas.getContext('2d');
  
    const blendedData = blendedCtx.createImageData(width, height);
  
    for (let i = 0; i < imgData1.data.length; i += 4) {
      const fg = imgData1.data.slice(i, i + 4);
      const bg = imgData2.data.slice(i, i + 4);
      const [r, g, b, a] = blendPixels(fg, bg);
      blendedData.data[i] = r;
      blendedData.data[i + 1] = g;
      blendedData.data[i + 2] = b;
      blendedData.data[i + 3] = a;
    }
  
    blendedCtx.putImageData(blendedData, 0, 0);
  
    const link = document.createElement('a');
    link.download = 'result.png';
    link.href = blendedCanvas.toDataURL();
    link.click();
  }

/**
 * 
 * @param {HTMLCanvasElement} canvas 
 * @param {*} image 
 */
export function changeImage(canvas, start, end, styleRatio = 1.0) {
  const x1 = start.x;
  const y1 = start.y;
  const x2 = end.x;
  const y2 = end.y;

  const x = Math.min(x1, x2);
  const y = Math.min(y1, y2);
  const selWidth = Math.abs(x2 - x1);
  const selHeight = Math.abs(y2 - y1);

  const ctx = canvas.getContext('2d');
  const selection = ctx.getImageData(x, y, selWidth, selHeight);

  let paddedWidth = selWidth;
  let paddedHeight = selHeight;

  const currentRatio = selWidth / selHeight;

  if (currentRatio > styleRatio) {
      paddedHeight = selWidth / styleRatio;
  } else {
      paddedWidth = selHeight * styleRatio;
  }

  const paddedCanvas = document.createElement('canvas');
  paddedCanvas.width = paddedWidth;
  paddedCanvas.height = paddedHeight;

  const paddedCtx = paddedCanvas.getContext('2d');

  const dx = (paddedWidth - selWidth) / 2;
  const dy = (paddedHeight - selHeight) / 2;

  paddedCtx.putImageData(selection, dx, dy);

  return {
    'image':paddedCanvas.toDataURL('image/png'),
    'padding':{'h':paddedHeight-selHeight,'w':paddedWidth-selWidth}
  }
}

export function getImageFromCanvas(canvas) {
    return canvas.toDataURL('image/png')
}

/**
 * 
 * @param {*} backup 
 * @param {ImageData} imageData
 * @param {HTMLCanvasElement} canvas 
 */
export function clearZoom(backup,imageData,canvas)
{
  if(imageData.width === canvas.width || imageData.height === canvas.height)
      return canvas.toDataURL('image/png')

  const ctx = canvas.getContext('2d') 
  const x1 = backup.start.x;
  const y1 = backup.start.y;
  const x2 = backup.end.x;
  const y2 = backup.end.y;
  const padW = backup.padding.w
  const padH = backup.padding.h
  
  const x = Math.min(x1, x2);
  const y = Math.min(y1, y2);
  const selWidth = Math.abs(x2 - x1);
  const selHeight = Math.abs(y2 - y1);
  const selection = ctx.getImageData(padW/2,padH/2,selWidth,selHeight)
  canvas.width = imageData.width
  canvas.height = imageData.height
  ctx.putImageData(imageData,0,0)
  ctx.putImageData(selection,x,y)

  return canvas.toDataURL('image/png')
}

export function rewriteCanvas(canvas,imageString)
{
    const img = new Image();

    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      canvas.getContext('2d').drawImage(img, 0, 0);
    };

    img.src = imageString;
}

export function denormalizeImage(data,a,b)
{
  for (let i = 0; i < data.length; i += 4) {
    data[i] = ((data[i]/255)*(b-a))+a
    data[i + 1] = ((data[i+1]/255)*(b-a))+a
    data[i + 2] = ((data[i+2]/255)*(b-a))+a
  }
}

function mean(arr) {
  let sum = 0;
  for (let v of arr) sum += v;
  return sum / arr.length;
}

function std(arr, meanVal) {
  let sumSq = 0;
  for (let v of arr) sumSq += (v - meanVal) ** 2;
  return Math.sqrt(sumSq / arr.length);
}

function updateMinMax(val,data)
{
  if(data<val.a)
    val.a = data
  if(data>val.b)
    val.b = data
}

function clamp(val, min, max) {
  return Math.max(min, Math.min(max, val));
}

function limit(val,limit)
{
  const sign = val<1?1:-1
  if(Math.abs(val)>limit)
    return limit*sign
  return val
}

/**
 * 
 * @param {HTMLCanvasElement} canvas 
 * @param {Number} a 
 * @param {Number} b 
 */
export function standardizeImage(canvas,a,b,method='minmax')
{
  // clamp
  // outlier
  // minmax
  
  const ctx = canvas.getContext('2d')
  const imageData = ctx.getImageData(0,0,canvas.width,canvas.height)
  const data = imageData.data

  const length = data.length / 4; 
  const reds = new Float32Array(length);
  const greens = new Float32Array(length);
  const blues = new Float32Array(length);

  const valR = {'a':data[0],'b':data[0]}
  const valG = {'a':data[1],'b':data[1]}
  const valB = {'a':data[2],'b':data[2]}

  for (let i = 0, j = 0; i < data.length; i += 4, j++) {
    reds[j] = data[i];
    greens[j] = data[i + 1];
    blues[j] = data[i + 2];

    if(method==='minmax')
    {
      updateMinMax(valR,reds[j])
      updateMinMax(valG,reds[j])
      updateMinMax(valB,reds[j])
    }
    
  }


  const meanR = mean(reds);
  const meanG = mean(greens);
  const meanB = mean(blues);


  const stdR = std(reds, meanR);
  const stdG = std(greens, meanG);
  const stdB = std(blues, meanB);

  valR.a = ( valR.a- meanR) / stdR
  valR.b = ( valR.b- meanR) / stdR
  valG.a = ( valG.a- meanG) / stdG
  valG.b = ( valG.b- meanG) / stdG
  valB.a = ( valB.a- meanB) / stdB
  valB.b = ( valB.b- meanB) / stdB

  for (let i = 0, j = 0; i < data.length; i += 4, j++) {
    if(method==='minmax')
    {
      data[i] = ((((reds[j] - meanR) / stdR)-valR.a)/(valR.b-valB.a))*255
      data[i + 1] = ((((greens[j] - meanG) / stdG)-valG.a)/(valG.b-valG.a))*255
      data[i + 2] = ((((blues[j] - meanB) / stdB)-valB.a)/(valB.b-valB.a))*255
    }
    else if(method==='clamp')
    {
      data[i] = clamp(((reds[j] - meanR) / stdR) * 128 + 128, 0, 255);
      data[i + 1] = clamp(((greens[j] - meanG) / stdG) * 128 + 128, 0, 255);
      data[i + 2] = clamp(((blues[j] - meanB) / stdB) * 128 + 128, 0, 255);
    }
    else
    {
      data[i] = (limit(reds[j],3*stdR)-3*stdR)*255
      data[i + 1] = (limit(greens[j],3*stdG)-3*stdG)*255
      data[i + 2] = (limit(blues[j],3*stdB)-3*stdB)*255
    }
  }
  ctx.putImageData(imageData, 0, 0);
}

/**
 * 
 * @param {HTMLCanvasElement} canvas 
 * @param {Number} a 
 * @param {Number} b 
 */
export function pozitiveActivations(canvas,a,b)
{
  const ctx = canvas.getContext('2d')
  const imageData = ctx.getImageData(0,0,canvas.width,canvas.height)
  const data = imageData.data

  const th = ((-a)/(b-a))*255
  for (let i = 0; i < data.length; i += 4) {
    data[i] = data[i]<=th?0:data[i]
    data[i+1] = data[i+1]<=th?0:data[i+1]
    data[i+2] = data[i+2]<=th?0:data[i+2]
  } 

  ctx.putImageData(imageData, 0, 0);
}

/**
 * 
 * @param {HTMLCanvasElement} canvas 
 * @param {Number} a 
 * @param {Number} b 
 */
export function negativeActivations(canvas,a,b)
{
  const ctx = canvas.getContext('2d')
  const imageData = ctx.getImageData(0,0,canvas.width,canvas.height)
  const data = imageData.data

  const th = ((-a)/(b-a))*255
  for (let i = 0; i < data.length; i += 4) {
    data[i] = data[i]>=th?0:data[i]
    data[i+1] = data[i+1]>=th?0:data[i+1]
    data[i+2] = data[i+2]>=th?0:data[i+2]
  } 

  ctx.putImageData(imageData, 0, 0);
}

/**
 * 
 * @param {HTMLCanvasElement} canvas 
 * @param {Number} a 
 * @param {Number} b 
 */
export function absoluteImage(canvas,a,b)
{
  const ctx = canvas.getContext('2d')
  const imageData = ctx.getImageData(0,0,canvas.width,canvas.height)
  const data = imageData.data 
  const newMax = Math.max(Math.abs(a),Math.abs(b))
  for (let i = 0; i < data.length; i += 4) {
    data[i] = Math.abs((((data[i]/255)*(b-a))+a))/newMax*255
    data[i + 1] = Math.abs((((data[i+1]/255)*(b-a))+a))/newMax*255
    data[i + 2] = Math.abs((((data[i+2]/255)*(b-a))+a))/newMax*255
  }

  ctx.putImageData(imageData, 0, 0);
}

/**
 * 
 * @param {HTMLCanvasElement} canvas 
 * @param {Number} a 
 * @param {Number} b 
 */
export function absStdImage(canvas,a,b,method='minmax')
{
  standardizeImage(canvas,a,b,method)
  const ctx = canvas.getContext('2d')
  const imageData = ctx.getImageData(0,0,canvas.width,canvas.height)
  const data = imageData.data
  for (let i = 0; i < data.length; i += 4) {
      data[i] = Math.abs(data[i]-128)+127
      data[i+1] = Math.abs(data[i+1]-128)+127
      data[i+2] = Math.abs(data[i+2]-128)+127
  }

  ctx.putImageData(imageData, 0, 0);
}

/**
 * 
 * @param {HTMLCanvasElement} canvas 
 * @param {*} th 
 */
export function overlay(canvas,th=127)
{
  const ctx = canvas.getContext('2d');
  const imageData = ctx.getImageData(0,0,canvas.width,canvas.height)
  const data = imageData.data;

    for (let i = 0; i < data.length; i += 4) {
      if(data[i]<th)
      {
        data[i] = 0
        data[i+1] = 0
        data[i+2] = 0
        data[i+3] = 0
      }
  }

  ctx.putImageData(imageData,0,0)

}

export function rgbToHex(r, g, b) {
  return "#" + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('');
}

export function eraseAt(ctx,x, y, size) {
  ctx.clearRect(x - size / 2, y - size / 2, size, size);
}

export function applyCorrection(canvas,a,b,correction)
{
  switch(correction)
  {
    case 'pozitive':
      pozitiveActivations(canvas,a,b);
      break;
    
    case 'negative':
      negativeActivations(canvas,a,b);
      break;
    
    case 'absolute':
      absoluteImage(canvas,a,b);
      break;
    
    case 'standard-absolute':
      absStdImage(canvas,a,b);
      break;

    default:
      standardizeImage(canvas,a,b);
  }
}

export function getItemFromNiiCol(i, j, k, shape, array) {
  const index = i + j * shape[0] + k * shape[0] * shape[1];
  return array[index];
}
export function getItemFromNii(i, j, k, shape, array) {
  const index = i * (shape[1] * shape[2]) + j * shape[2] + k;
  return array[index];
}

function getElementFromAxis(axis, sliceIndex, i, j, array, shape,type='') {
  let funRef = type!=='col'?getItemFromNii:getItemFromNiiCol;


  if (axis === 0)
    return funRef(sliceIndex, i, j, shape, array);
  if (axis === 1)
    return funRef(i, sliceIndex, j, shape, array);
  return funRef(i, j, sliceIndex, shape, array);
}

export function getSliceFromNii(sliceIndex, axis, array, shape) {
  const keep = [];
  for (let i = 0; i < 3; i++) {
    if (i !== axis) keep.push(shape[i]);
  }

  const width = keep[0];
  const height = keep[1];

  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');
  const imageData = ctx.getImageData(0, 0, width, height);
  const data = imageData.data;

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const index = (y * width + x) * 4;
      const val = getElementFromAxis(axis, sliceIndex, x, y, array, shape,'col');
      data[index]     = val;
      data[index + 1] = val;
      data[index + 2] = val;
      data[index + 3] = 255;
    }
  }


  ctx.putImageData(imageData, 0, 0);
  return getImageFromCanvas(canvas);
}

export function getMaskFromNii(sliceIndex, axis, array, shape) 
{
  const keep = [];
  for (let i = 0; i < 3; i++) {
    if (i !== axis) keep.push(shape[i]);
  }

  const width = keep[0];
  const height = keep[1];

  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');
  const imageData = ctx.getImageData(0, 0, width, height);
  const data = imageData.data;

  const cmap = {
    0:[0,0,0,0],
    1:[255,0,0,255],
    2:[0,255,0,255],
    3:[0,0,255,255],
  }


  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const index = (y * width + x) * 4;
      const val = getElementFromAxis(axis, sliceIndex, x, y, array, shape);
      const color = cmap[val]
      data[index]     = color[0];
      data[index + 1] = color[1];
      data[index + 2] = color[2];
      data[index + 3] = color[3];
    }
  }

  ctx.putImageData(imageData, 0, 0);
  return getImageFromCanvas(canvas);
}