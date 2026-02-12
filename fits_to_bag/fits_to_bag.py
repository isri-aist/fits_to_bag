from astropy.io import fits
import glob
import rclpy
from rclpy.node import Node
from tqdm import tqdm
import rosbag2_py
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from pathlib import Path
import time
from rclpy.serialization import serialize_message


class FitsToRosbagNode(Node):
    def __init__(self):
        super().__init__('fits_to_rosbag_node')
        
        # Declare parameters
        self.declare_parameter('fits_folder', '/tmp/FITS')
        self.declare_parameter('output_bag', '/tmp/output.bag')
        
        self.fits_folder = self.get_parameter('fits_folder').value
        self.output_bag = self.get_parameter('output_bag').value
        self.bridge = CvBridge()
        
    def get_fits_files(self):
        """Scan folder for FITS files"""
        pattern = str(Path(self.fits_folder) / "*.fits")
        return sorted(glob.glob(pattern))
    
    def extract_header_info(self, fits_file):
        """Extract relevant info from FITS header"""
        with fits.open(fits_file) as hdul:
            header = hdul[0].header
            info = {
                'bayerp': header.get('BAYERP', None),
                'colortyp': header.get('COLORTYP', None),
                'fps': header.get('FPS', 30),
                'xpixsz': header.get('XPIXSZ', None),
                'ypixsz': header.get('YPIXSZ', None),
                'fov': header.get('FOV', None),
                'exposure': header.get('EXPOSURE', None),
            }
            data = hdul[0].data
        return info, data
    
    def process(self):
        """Main processing function"""
        fits_files = self.get_fits_files()
        
        if not fits_files:
            self.get_logger().error(f"No FITS files found in {self.fits_folder}")
            return
        
        # Extract info from first image
        info, _ = self.extract_header_info(fits_files[0])
        self.get_logger().info(f"Header info: {info}")
        
        fps = info['fps']
        frame_interval_ns = int(1e9 / fps)
        start_time_ns = int(time.time() * 1e9)
        
        # Create rosbag
        writer = rosbag2_py.SequentialWriter()
        writer.open(rosbag2_py.StorageOptions(uri=self.output_bag, storage_id='sqlite3'),
                    rosbag2_py.ConverterOptions('cdr', 'cdr'))
        
        topic_name = '/camera/image_raw'
        topic_info = rosbag2_py.TopicMetadata(
            name=topic_name,
            type='sensor_msgs/msg/Image',
            serialization_format='cdr'
        )
        writer.create_topic(topic_info)

        once = True
        
        # Write images to rosbag
        for idx, fits_file in enumerate(tqdm(fits_files, desc="Processing FITS files")):
            try:
                # pass
                _, data = self.extract_header_info(fits_file)

                if once:
                    once = False
                    print(f"shape {data.shape}, dtype {data.dtype}, byte order {data.dtype.byteorder}")


                msg = self.bridge.cv2_to_imgmsg(data, encoding="mono16")

                current_timestamp_ns = start_time_ns + (idx * frame_interval_ns)
                msg.header.stamp.sec = current_timestamp_ns // 10**9
                msg.header.stamp.nanosec = current_timestamp_ns % 10**9
                msg.header.frame_id = "camera_optical_frame"

                writer.write(topic_name, serialize_message(msg), current_timestamp_ns)

            except Exception as e:
                self.get_logger().warn(f"Error processing {fits_file}: {e}")
        
        writer.close()
        self.get_logger().info(f"Rosbag saved to {self.output_bag}")


def main():
    try:
        rclpy.init()
        node = FitsToRosbagNode()
        node.process()
        rclpy.shutdown()
    except Exception as e:
        print(f"Node error {e}")


if __name__ == "__main__":
    main()
    