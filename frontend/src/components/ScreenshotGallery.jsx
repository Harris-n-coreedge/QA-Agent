import { useState } from 'react'
import { Image, X, Download, ZoomIn, ChevronLeft, ChevronRight, Maximize2 } from 'lucide-react'

export function ScreenshotGallery({ screenshots = [], title = 'Screenshots' }) {
  const [lightbox, setLightbox] = useState({ open: false, index: 0 })

  if (!screenshots || screenshots.length === 0) {
    return null
  }

  const openLightbox = (index) => {
    setLightbox({ open: true, index })
  }

  const closeLightbox = () => {
    setLightbox({ open: false, index: 0 })
  }

  const nextImage = () => {
    setLightbox((prev) => ({
      ...prev,
      index: (prev.index + 1) % screenshots.length,
    }))
  }

  const prevImage = () => {
    setLightbox((prev) => ({
      ...prev,
      index: prev.index === 0 ? screenshots.length - 1 : prev.index - 1,
    }))
  }

  const handleDownload = (url, filename) => {
    const link = document.createElement('a')
    link.href = url
    link.download = filename || `screenshot-${Date.now()}.png`
    link.click()
  }

  return (
    <>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="text-base font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <Image className="w-5 h-5" />
            {title} ({screenshots.length})
          </h4>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {screenshots.map((screenshot, index) => {
            const url = typeof screenshot === 'string' ? screenshot : screenshot.url || screenshot
            const alt = typeof screenshot === 'object' ? screenshot.alt || screenshot.name : 'Screenshot'
            
            return (
              <div
                key={index}
                className="group relative aspect-video rounded-lg overflow-hidden border border-slate-200 dark:border-slate-700 cursor-pointer hover:border-indigo-500 transition-all"
              >
                <img
                  src={url}
                  alt={alt}
                  className="w-full h-full object-cover"
                  onClick={() => openLightbox(index)}
                />
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-colors flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      openLightbox(index)
                    }}
                    className="p-2 rounded-full bg-white/90 hover:bg-white text-slate-900"
                    title="View full size"
                  >
                    <ZoomIn className="w-4 h-4" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDownload(url, `screenshot-${index + 1}.png`)
                    }}
                    className="p-2 rounded-full bg-white/90 hover:bg-white text-slate-900"
                    title="Download"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Lightbox */}
      {lightbox.open && (
        <div className="fixed inset-0 z-[10000] bg-black/95 flex items-center justify-center">
          <button
            onClick={closeLightbox}
            className="absolute top-4 right-4 p-2 rounded-full bg-white/10 hover:bg-white/20 text-white z-50"
          >
            <X className="w-6 h-6" />
          </button>

          <button
            onClick={prevImage}
            className="absolute left-4 p-3 rounded-full bg-white/10 hover:bg-white/20 text-white z-50"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>

          <button
            onClick={nextImage}
            className="absolute right-4 p-3 rounded-full bg-white/10 hover:bg-white/20 text-white z-50"
          >
            <ChevronRight className="w-6 h-6" />
          </button>

          <div className="max-w-7xl max-h-[90vh] p-8">
            <img
              src={typeof screenshots[lightbox.index] === 'string' 
                ? screenshots[lightbox.index] 
                : screenshots[lightbox.index]?.url || screenshots[lightbox.index]}
              alt={`Screenshot ${lightbox.index + 1}`}
              className="max-w-full max-h-full object-contain rounded-lg"
            />
            <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex items-center gap-2 px-4 py-2 rounded-lg bg-black/50 text-white text-sm">
              {lightbox.index + 1} / {screenshots.length}
            </div>
          </div>

          {/* Keyboard navigation */}
          <div
            className="absolute inset-0"
            onKeyDown={(e) => {
              if (e.key === 'ArrowLeft') prevImage()
              if (e.key === 'ArrowRight') nextImage()
              if (e.key === 'Escape') closeLightbox()
            }}
            tabIndex={0}
          />
        </div>
      )}
    </>
  )
}




