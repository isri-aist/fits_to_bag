# fits_to_bag
# FitsToRosbag ROS2 Node Documentation

## Overview
This ROS2 node converts FITS (Flexible Image Transport System) format astronomical/RAW images into a ROS2 bag file. It reads FITS files from a specified directory, extracts metadata from FITS headers, and publishes the image data as ROS2 Image messages with appropriate timestamps.

## Node Information
- **Node Name**: `fits_to_rosbag_node`
- **Published Topics**: `/camera/image_raw` (sensor_msgs/msg/Image)
- **Message Format**: mono16 (16-bit grayscale)
- **Output Format**: SQLite3 ROS2 bag file

## Parameters

### `fits_folder`
- **Type**: string
- **Default**: `/tmp/FITS`
- **Description**: Path to the directory containing FITS files to process. All `.fits` files in this directory will be converted and included in the output bag.

### `output_bag`
- **Type**: string
- **Default**: `/tmp/output.bag`
- **Description**: Path and filename for the output ROS2 bag file. The file will be created in SQLite3 format.

## FITS Header Fields Used
The node extracts the following optional fields from FITS headers:
- `BAYERP`: Bayer pattern information
- `COLORTYP`: Color type information
- `FPS`: Frames per second (default: 30)
- `XPIXSZ`: X pixel size
- `YPIXSZ`: Y pixel size
- `FOV`: Field of view
- `EXPOSURE`: Exposure time

## Usage

### Basic Usage

```bash
ros2 run fits_to_bag fits_to_rosbag_node --ros-args -p fits_folder:=/path/to/fits/files -p output_bag:=/path/to/output.bag
```

### Advanced Usage

```bash
ros2 run fits_to_bag fits_to_rosbag_node --ros-args \
    -p fits_folder:=/home/user/astronomy/data \
    -p output_bag:=/home/user/bags/observation_2024.bag
```

### Verify Output

```bash
ros2 bag info /path/to/output.bag
```
