// An apps script for google slides that collects youtube links from embedded videos in a presentation along with any image on each slide


function getYouTubeLinks() {
    var presentation = SlidesApp.getActivePresentation();
    var slides = presentation.getSlides();
    var links = [];

    slides.forEach(function(slide) {
        var elements = slide.getPageElements();
        elements.forEach(function(element) {
            if (element.getPageElementType() === SlidesApp.PageElementType.VIDEO) {
                var video = element.asVideo();
                var videoId = video.getVideoId();
                if (videoId) {
                    var videoUrl = "https://www.youtube.com/watch?v=" + videoId;
                    // Check if videoUrl is already in the links array
                    if (links.indexOf(videoUrl) === -1) { 
                        links.push(videoUrl);
                    }
                }
            }
        });
    });

    Logger.log(links.join("\n")); // Output in the Apps Script Logger
    return links;
}

function getImages() {
    var presentation = SlidesApp.getActivePresentation();
    var slides = presentation.getSlides();
    var folderName = "Extracted Images"; // Change if needed
    var folder, folders = DriveApp.getFoldersByName(folderName);

    // Check if the folder exists, otherwise create it
    if (folders.hasNext()) {
        folder = folders.next();
    } else {
        folder = DriveApp.createFolder(folderName);
    }

    var sampleNumber = "000"; // Default sample number
    var ignoredSlides = 8; // Ignore the first 8 slides

    slides.forEach(function(slide, slideIndex) {
        if (slideIndex < ignoredSlides) return; // Skip first 8 slides

        var elements = slide.getPageElements();
        var initials = ""; // Default empty initials
        
        elements.forEach(function(element) {
            if (element.getPageElementType() === SlidesApp.PageElementType.SHAPE) {
                var text = element.asShape().getText().asString().trim();
                
                // Check if the text contains "Sample #"
                var sampleMatch = text.match(/Sample #(\d+)/);
                if (sampleMatch) {
                    sampleNumber = ("000" + sampleMatch[1]).slice(-3); // Ensure 3-digit format
                }

                // Assume initials are at the top of the slide (2-3 letters)
                var initialsMatch = text.match(/^[A-Z]{2,3}$/i); // Matches 2-3 letter initials
                if (initialsMatch) {
                    initials = initialsMatch[0].toUpperCase();
                }
            }
        });

        // Extract images from the slide
        elements.forEach(function(element, elemIndex) {
            if (element.getPageElementType() === SlidesApp.PageElementType.IMAGE) {
                var imageBlob = element.asImage().getBlob();
                
                // Construct file name: s[number]_[initials].jpg
                var fileName = "s" + sampleNumber + "_" + initials + ".jpg";
                var file = folder.createFile(imageBlob.setName(fileName));
            }
        });
    });
    return;
}