# -*- coding: utf-8 -*-

# Pain Indication Area Analysis

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Slider
from math import atan2

# 1. Data Processing

def load_and_process_data_adjusted(filename, img_shape):
    """
    Load the data and adjust the y-coordinates based on the height of the image.
    """
    with open(filename, "r") as file:
        data_content = file.readlines()
    coordinates = []
    for line in data_content:
        parts = line.strip().split(",")
        if len(parts) == 2 and "**" not in line:
            x, y = map(int, parts)
            y = img_shape[0] - y  # Flip the y-coordinate
            coordinates.append((x, y))
    return coordinates

# 2. Convex Hull Generation
def graham_scan(points):
    def cross_product(o, a, b):
        return (a[0]-o[0]) * (b[1]-o[1]) - (b[0]-o[0]) * (a[1]-o[1])
    def distance(p1, p2):
        return (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2
    start = min(points, key=lambda point: (point[1], point[0]))
    sorted_points = sorted(points, key=lambda point: (atan2(point[1]-start[1], point[0]-start[0]), distance(start, point)))
    unique_angles_points = [sorted_points[0]]
    for p in sorted_points[1:]:
        while len(unique_angles_points) > 1 and cross_product(unique_angles_points[-2], unique_angles_points[-1], p) == 0:
            unique_angles_points.pop()
        unique_angles_points.append(p)
    hull = unique_angles_points[:2]
    for p in unique_angles_points[2:]:
        while len(hull) > 1 and cross_product(hull[-2], hull[-1], p) <= 0:
            hull.pop()
        hull.append(p)
    return hull

# 3. Overlap Analysis
def line_intersection(line1, line2):
    x_diff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    y_diff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])
    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]
    div = det(x_diff, y_diff)
    if div == 0:
        return None
    d = (det(*line1), det(*line2))
    x = det(d, x_diff) / div
    y = det(d, y_diff) / div
    return x, y

def sutherland_hodgman(subject_polygon, clipping_polygon):
    output_list = subject_polygon
    def inside(p, cp1, cp2):
        return (cp2[0]-cp1[0]) * (p[1]-cp1[1]) > (cp2[1]-cp1[1]) * (p[0]-cp1[0])
    for clip_vertex1, clip_vertex2 in zip(clipping_polygon, clipping_polygon[1:] + [clipping_polygon[0]]):
        input_list = output_list
        output_list = []
        s = input_list[-1]
        for e in input_list:
            if inside(e, clip_vertex1, clip_vertex2):
                if not inside(s, clip_vertex1, clip_vertex2):
                    intersection = line_intersection((clip_vertex1, clip_vertex2), (s, e))
                    if intersection:
                        output_list.append(intersection)
                output_list.append(e)
            elif inside(s, clip_vertex1, clip_vertex2):
                intersection = line_intersection((clip_vertex1, clip_vertex2), (s, e))
                if intersection:
                    output_list.append(intersection)
            s = e
    return output_list

# 4. Visualization
def dynamic_intersection(polygons):
    """Dynamically compute the intersection region based on the provided polygons."""
    intersection_region = polygons[0]
    for poly in polygons[1:]:
        intersection_region = sutherland_hodgman(intersection_region, poly)
    return intersection_region

def visualize_polygons_on_image(polygons, image_path, labels=None):
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.subplots_adjust(bottom=0.25)
    img = plt.imread(image_path)
    ax.imshow(img, extent=[0, img.shape[1], 0, img.shape[0]])
    colors = ['blue', 'green', 'red', 'purple', 'yellow', 'cyan']
    def set_axis_limits():
        ax.set_xlim(0, img.shape[1])
        ax.set_ylim(0, img.shape[0])
    def draw_polygons(threshold):
        ax.clear()
        ax.imshow(img, extent=[0, img.shape[1], 0, img.shape[0]])
        set_axis_limits()
        current_polygons = polygons[:threshold]
        for idx, polygon in enumerate(current_polygons):
            polygon_path = patches.Polygon(polygon, closed=True, fill=False, edgecolor=colors[idx % len(colors)], linewidth=1.5)
            ax.add_patch(polygon_path)
            if labels:
                plt.text(polygon[0][0], polygon[0][1], labels[idx], color=colors[idx % len(colors)], weight='bold')
        if len(current_polygons) > 1:
            intersection_region = dynamic_intersection(current_polygons)
            intersection_path = patches.Polygon(intersection_region, closed=True, fill=True, color='grey', alpha=0.5)
            ax.add_patch(intersection_path)
        ax.grid(True)
        plt.draw()
    def update(val):
        threshold = int(slider.val)
        draw_polygons(threshold)
    draw_polygons(len(polygons))  # Draw all polygons initially
    ax_slider = plt.axes([0.2, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    slider = Slider(ax_slider, 'Polygon Count', 1, len(polygons), valinit=len(polygons), valstep=1)
    slider.on_changed(update)
    plt.xlabel('X-coordinate')
    plt.ylabel('Y-coordinate')
    plt.title('Visualization of Convex Hulls with Slider on Image')
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

# Process the data, generate convex hulls, and calculate intersections
data_files_prefixed = [
    "1_96741889266.txt", "1_96741889870.txt", 
    "1_96741890249.txt", "1_96741890620.txt", 
    "1_96741890844.txt", "1_96741891097.txt"
]

def adjust_coordinates(data, img_shape, x_scale=1.0, y_scale=1.0, x_offset=0, y_offset=0):
    """
    Adjust the data coordinates based on scale and offset values.
    """
    adjusted_data = []
    for (x, y) in data:
        x_adj = (x * x_scale) + x_offset
        y_adj = (y * y_scale) + y_offset
        adjusted_data.append((x_adj, y_adj))
    return adjusted_data



# Get the shape of the image to know its height
img = plt.imread('LeftSideView.png')
img_shape = img.shape

# Extract bounding box information from the FootViewData.txt file
def extract_foot_view_data(filename):
    with open(filename, "r") as file:
        data_content = file.readlines()
    for line in data_content:
        if "Type1:" in line:
            bbox_data = line.strip().split(":")[1]
            return list(map(int, bbox_data.split(',')))
    return []

# Extract the bounding box for the foot view
foot_bbox = extract_foot_view_data("FootViewData.txt")
foot_bbox


# Extract the bounding box coordinates for the foot region
x1, y1, x2, y2 = foot_bbox

# Calculate the width and height of the bounding box
bbox_width = x2 - x1
bbox_height = y2 - y1

# Determine the scaling factors based on the bounding box dimensions
x_scale_bbox = bbox_width / img_shape[1]
y_scale_bbox = bbox_height / img_shape[0]

# Adjust the scale and offset values to fit within the bounding box
x_scale_adjustment = x_scale_bbox
y_scale_adjustment = y_scale_bbox
x_offset_adjustment = x1
y_offset_adjustment = y1

data_hulls_bbox_adjusted = []
for filename in data_files_prefixed:
    data = load_and_process_data_adjusted(filename, img_shape)
    data_adjusted = adjust_coordinates(data, img_shape, 
                                       x_scale_adjustment, y_scale_adjustment, 
                                       x_offset_adjustment, y_offset_adjustment)
    data_hulls_bbox_adjusted.append(graham_scan(data_adjusted))
intersection_region_bbox_adjusted = data_hulls_bbox_adjusted[0]
for hull in data_hulls_bbox_adjusted[1:]:
    intersection_region_bbox_adjusted = sutherland_hodgman(intersection_region_bbox_adjusted, hull)
all_regions_bbox_adjusted = data_hulls_bbox_adjusted + [intersection_region_bbox_adjusted]


# Define the labels for visualization
labels = ["Hull 1", "Hull 2", "Hull 3", "Hull 4", "Hull 5", "Hull 6", "Intersection"]


# Visualize the convex hulls and their intersection on the image with adjusted y-coordinates
visualize_polygons_on_image(all_regions_bbox_adjusted, 'LeftSideView.png', labels=labels)


