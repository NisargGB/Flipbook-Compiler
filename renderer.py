import argparse
import cv2
import numpy as np
import os


class Compiler:
    def __init__(self, resource_dir='.'):
        self.frame_size = (512, 512)             # the rendering frame size (H, W)
        self.lines = []                          # The list of lines of code
        self.counter = 0                         # The program counter - line number
        self.frames = []                         # A list of images (H, W, BGR) to display in sequence frame by frame
        self.resource_dir = resource_dir         # Directory containing the source images


    def display_frame(self, frame):
        """
        For displaying a frame while debugging
        """
        cv2.imshow("Frame", frame)
        cv2.waitKey(0)


    def display_frames(self):
        """
        For displaying all frames one by one while debugging
        """
        for frame in self.frames:
            self.display_frame(frame)


    def compilation_error(self, error):
        """
        Raises a compilation error with given error message and terminates the program
        """
        print("Compilation Failed")
        print("Error", error, "at line", str(self.counter))
        exit(1)


    def get_image(self, img_path):
        """
        Returns a 4-channel image array (H, W, BGRA) at givn image path
        """
        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        # Check if image exists
        if img is None:
            self.compilation_error("Resource error")
        
        # Add alpha channel if required
        if img.shape[-1] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        return img


    def parse_frame_size(self):
        """
        The counter is at line containing 'frame_size'
        Format: frame_size <Height> <Width>
        """
        line = self.lines[self.counter]
        content = line.split()
        try:
            height = int(content[1])
            width = int(content[2])
            self.frame_size = (height, width)
        except ValueError:
            self.compilation_error("Frame size error")


    def parse_show(self):
        """
        The self.counter is at a line containing 'show' command
        Format: show <img.jpg> <start_frame> <end_frame> <scale> <top_offset> <right_offset>
        """
        line = self.lines[self.counter]
        content = line.split()

        fpath = os.path.join(resource_dir, content[1])

        start_frame = 0              # default values
        end_frame = 1
        toff = 0
        roff = 0
        scale = 1.0
        try:
            start_frame = int(content[2])
            end_frame = int(content[3])
            scale = float(content[4])
            toff = int(content[5])
            roff = int(content[6])
        except ValueError:
            self.compilation_error("Parsing Error")

        self.implement_show(fpath, start_frame, end_frame, scale, toff, roff)


    def implement_show(self, fpath, start_frame, end_frame, scale, toff, roff):
        """
        Executes the show command
        """
        # Fetching the source image
        img = self.get_image(fpath)
        new_size = (int(img.shape[1] * scale), int(img.shape[0] * scale))
        img = cv2.resize(img, new_size)
        if len(self.frames) < end_frame:
            blank_img = np.zeros((self.frame_size[0], self.frame_size[1], 4), np.uint8)
            blank_img[..., 3] = 255
            diff = [blank_img.copy() for _ in range(end_frame - len(self.frames))]
            self.frames.extend(diff)

        # Placed out of bounds
        if toff >= self.frame_size[0] or roff >= self.frame_size[1] or toff < -img.shape[0] or roff < -img.shape[1]:
            return

        # Modifying the desired list of frames
        bgx1 = max(0, toff)
        bgy1 = max(0, roff)
        bgx2 = min(self.frame_size[0], toff + img.shape[0])
        bgy2 = min(self.frame_size[1], roff + img.shape[1])
        fgx1 = max(0, -toff)
        fgy1 = max(0, -roff)
        fgx2 = min(img.shape[0], self.frame_size[0] - toff)
        fgy2 = min(img.shape[1], self.frame_size[1] - roff)
        alpha_fg = np.expand_dims(img[fgx1:fgx2, fgy1:fgy2, 3] / 255, axis=-1)
        alpha_bg = 1 - alpha_fg
        for i in range(start_frame, end_frame):
            weighted = (alpha_bg * self.frames[i][bgx1:bgx2, bgy1:bgy2, :3] + alpha_fg * img[fgx1:fgx2, fgy1:fgy2, :3])
            weighted = np.clip(weighted, 0., 255.)
            self.frames[i][bgx1:bgx2, bgy1:bgy2, :3] = weighted.astype(np.uint8)


    def parse_move(self):
        """
        The self.counter is at a line containing 'show' command
        Format: move <img.jpg> <start_frame> <end_frame> <scale> <start_top_off> <start_right_off> <end_top_off> <end_right_off>
        """
        line = self.lines[self.counter]
        content = line.split()

        fpath = os.path.join(resource_dir, content[1])

        start_frame = 0              # default values
        end_frame = 1
        scale = 1.0
        stoff, sroff, etoff, eroff = 0, 0, 0, 0
        try:
            start_frame = int(content[2])
            end_frame = int(content[3])
            scale = float(content[4])
            stoff = int(content[5])
            sroff = int(content[6])
            etoff = int(content[7])
            eroff = int(content[8])
        except ValueError:
            self.compilation_error("Parsing Error")

        self.implement_move(fpath, start_frame, end_frame, scale, stoff, sroff, etoff, eroff)


    def implement_move(self, fpath, start_frame, end_frame, scale, stoff, sroff, etoff, eroff):
        """
        Executes the move command
        """
        # The amount by which the image moves in each frame
        tstep = (etoff - stoff) / (end_frame - 1 - start_frame)
        rstep = (eroff - sroff) / (end_frame - 1 - start_frame)
        toff_val, roff_val = stoff, sroff
        frame_num = start_frame

        # pdate the offset in each frame and place the image
        while toff_val <= etoff and roff_val <= eroff and frame_num < end_frame:
            toff = int(toff_val)
            roff = int(roff_val)
            self.implement_show(fpath, frame_num, frame_num+1, scale, toff, roff)

            frame_num += 1
            toff_val += tstep
            roff_val += rstep


    def parse_code(self, filepath):
        """
        Args: filepath - path to the file containing source code
        """

        # Read the entire file line by line
        with open(filepath) as fd:
            self.lines = fd.readlines()
        self.lines = [line.strip() for line in self.lines]

        # Parse each line of code
        begin = False
        for line in self.lines:
            print(self.counter, line)
            content = line.split()
            # if the first valid line contains frame size
            if content[0] == "frame_size" and not begin:
                self.parse_frame_size()
            # If the line is a show command
            elif content[0] == "show":
                self.parse_show()
            # If the line is a move command
            elif content[0] == "move":
                self.parse_move()
            # If the line contains invalid command
            elif content[0][0] != '#':
                self.compilation_error("Syntax Error")

            if content[0][0] != '#' and not begin:
                begin = True

            self.counter += 1
        # self.display_frames()


    def render_video(self, outfpath):
        """
        Saves the list of frames as an mp4 video
        """
        if len(self.frames) == 0:
            return

        height, width = self.frame_size
        fourcc = cv2.VideoWriter_fourcc(*'DIVX')
        video = cv2.VideoWriter(outfpath, fourcc, 15, (width, height))

        for i in range(len(self.frames)):
            video.write(self.frames[i][..., :3])
        
        video.release()
        cv2.destroyAllWindows()



if __name__ == "__main__":

    # Parse command line arguments
    argparser = argparse.ArgumentParser("Command line arguments")
    argparser.add_argument('codefilepath')
    argparser.add_argument('--resource_dir', dest='resource_dir', type=str, default=None)
    argparser.add_argument('--output', dest='outfilepath', type=str, default=None)
    args = argparser.parse_args()

    codef = args.codefilepath
    resource_dir = args.resource_dir
    outf = args.outfilepath

    # Instantiate compiler and compile the code
    magic = Compiler(resource_dir=resource_dir)
    magic.parse_code(codef)
    magic.render_video(outf)
