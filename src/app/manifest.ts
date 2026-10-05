import type { MetadataRoute } from 'next'

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'ARCS Field OS',
    short_name: 'ARCS',
    description: 'Navigate to clarity. Make the decision visible.',
    start_url: '/',
    display: 'standalone',
    background_color: '#020408',
    theme_color: '#020408',
    icons: [
      { src: '/icon.svg', sizes: 'any', type: 'image/svg+xml' },
      { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
      { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
    ],
  }
}
