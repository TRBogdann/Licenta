import './editor.css'
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ImageViewer2D from '../components/imageviewer/2D/imageviewer2d';
import EditorBar from '../components/editorbar/editorbar';

function Editor(props) {
    // 
    // settings:{imageType,setImageType,fileCount,setFileCount},
    // content:{images,setImages,effects,setEffects,ranges,setRanges,imgBackup,setImgBackup},
    // result:{probs,setProbs,labels,setLabels},
    // routes:serverRoute
    // 

    const settings = props.data.settings;
    const content = props.data.content;
    const contentMri = props.data.contentMri;
    const routes = props.data.routes;
    const result = props.data.result;

    const hasActivation = routes.activation;
    const hasMask = routes.mask;
    const dummyEvent = {preventDefault:()=>{}}

    const [overlay,setOverlay] = useState(0.5) 
    const [command, setCommand] = useState('');
    const [viewMode, setViewMode] = useState('normal')
    const [toolName, setToolName] = useState('select');
    const [color, setColor] = useState("#aabbcc");
    const [pensize, setPensize] = useState(1);
    const [cmap, setCmap] = useState('normal')
    const [correction, setCorrection] = useState('none');
    const [cursor, setCursor] = useState('');
    const [mode, setMode] = useState(hasMask ? 'mask' : 'activation')

    useEffect(() => {
        setToolName('select');
    }, [viewMode]);

    useEffect(() => {
        switch (command) {
            case 'get-activations':
                handleActivations(dummyEvent);
                break;
            
            case 'get-masks':
                handleMasks(dummyEvent);
                break;

            case 'delete-backup':
                content.setEffects([]);
                setCommand('');
                break;

            default:
        }
    }, [command])

    useEffect(() => {
        if (toolName !== 'select') {
            setCursor('paint-mode')
        }
        else {
            setCursor('');
        }
    }, [toolName])
    const data =
    {
        settings: { ...settings, viewMode, setViewMode, hasActivation, hasMask, mode, setMode, cursor, overlay, setOverlay},
        routes: routes,
        content: content,
        contentMri : contentMri,
        result: result,
        commandBox: { command, setCommand },
        tool: { toolName, setToolName, color, setColor, pensize, setPensize },
        palette: { cmap, setCmap, correction, setCorrection }
    }

    function getViewer(imageType) {
        switch (imageType) {
            case '3D':
                return (
                    <></>
                );

            default:
                return (
                    <ImageViewer2D data={data} />
                );
        }
    }

    const navigate = useNavigate();
    useEffect(() => {
        if (content.images.length < 1) {
            navigate('/tools', { replace: true });
        }
    })

    const handleMasks = async (e) => {
        e.preventDefault();
        if (!content.file)
            return
        const formData = new FormData();
        formData.append('image', content.file);
        try {
            const response = await fetch(routes.mask, {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            const roundedArray = data['probs'].map(num => Math.round(num * 100) / 100)
            content.setImgBackup([])
            content.setEffects([])
            result.setProbs(roundedArray)
            result.setLabels(data['classes'])
            const reader = new FileReader();
            reader.onload = function (event) {
                const newImages = [event.target.result];
                const newRanges = [{ a: 0, b: 255 }];
                for (let i = 1; i < data['size'] + 1; i++) {
                    newImages.push(data['img_' + i])
                    newRanges.push({ a: 0, b: 255 })
                }
                setCommand('reset-index');
                setMode('mask');
                content.setImages(newImages)
                content.setRanges(newRanges)
            };
            reader.readAsDataURL(content.file);

        } catch (error) {
            console.error('Error uploading image:', error);
        }
    }

    const handleActivations = async (e) => {
        e.preventDefault();
        if (!content.file)
            return
        const formData = new FormData();
        formData.append('image', content.file);
        try {
            const response = await fetch(routes.activation, {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            const roundedArray = data['probs'].map(num => Math.round(num * 100) / 100)
            content.setImgBackup([])
            content.setEffects([])
            result.setProbs(roundedArray)
            result.setLabels(data['classes'])
            const reader = new FileReader();
            reader.onload = function (event) {
                const newImages = [event.target.result]
                const newRanges = [{ a: 0, b: 255 }]
                for (let i = 1; i < data['size'] + 1; i++) {
                    newImages.push(data['img_' + i])
                    newRanges.push(data['range_' + i])
                }
                setCommand('reset-index');
                setMode('activation');
                content.setRanges(newRanges)
                content.setImages(newImages);
            };
            reader.readAsDataURL(content.file);


        } catch (error) {
            console.error('Error uploading image:', error);
        }
    }

    return (
        <div className="edit-image-container">
            {getViewer(settings.imageType)}
            <EditorBar data={data} />
        </div>
    )
}

export default Editor;