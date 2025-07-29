# NexaPod Globe Visualization

This document provides an overview of the interactive 3D globe feature on the NexaPod landing page.

## 1. Features

The globe visualization is built with `globe.gl` and `Three.js` to provide a dynamic and engaging representation of the NexaPod network.

*   **Interactive 3D Globe:** A draggable and zoomable 3D model of the Earth.
*   **Global Node Network:** Key cities around the world are represented as nodes on the globe. The size of each node is proportional to its simulated activity level (i.e., number of jobs).
*   **Simulated Network Traffic:** Animated arcs fly between nodes to represent compute jobs being sent across the network. This is a visual simulation to demonstrate the project's concept.
*   **Asynchronous Pulsing:** Nodes light up to indicate sending or receiving a "packet," creating a lively and asynchronous network effect.
*   **Theming:** The globe's aesthetic (atmosphere color, labels) is fully integrated with the site's theme switcher, offering multiple visual styles.
*   **Hover Interaction:** Hovering over a city's label will highlight it for better visibility.

## 2. How to Modify

The globe's logic is contained within a `<script>` tag in `index.html`.

### Adding or Changing Cities

To add, remove, or modify the nodes on the globe, locate the `cities` array inside the main script.

Each city is an object with the following properties:

```javascript
{
  lat: 40.7128,       // Latitude
  lng: -74.0060,      // Longitude
  jobs: 88,           // Simulated job count (influences node size)
  label: 'New York'   // Name displayed on hover
}
```

1.  **Find Coordinates:** Use an online tool to find the latitude and longitude of the city you wish to add.
2.  **Add to Array:** Add a new object with the correct data to the `cities` array.
3.  **Set Job Count:** Assign a `jobs` value. Higher numbers will result in a slightly larger node on the globe.

The script will automatically handle the rest, including scaling the node size and including it in the network pulse simulation.

