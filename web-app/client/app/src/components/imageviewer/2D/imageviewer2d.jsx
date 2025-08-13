import '../imageviewer.css'
import GridView from './viewers/grid';
import OneImageView from './viewers/oneimage';
import OverlayView from './viewers/overlay';



// settings: {...settings,viewMode,setViewMode,hasActivation,hasMask},
// routes: routes,
// content: content,
// result: result

function ImageViewer2D(props)
{
    function getViewer(viewMode) {
        switch (viewMode) {
            case 'grid':
                return (
                    <GridView data={props.data}/>
                )

            case 'overlay':
                return (
                    <OverlayView data={props.data}/>
                );
            default:
                return (
                    <OneImageView data={props.data}/>
                );
        }
    }
    return(
        <div>
            {getViewer(props.data.settings.viewMode)}
        </div>
    )
}

export default ImageViewer2D;