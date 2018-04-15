// http://adam.dominec.eu/proj/subre.html

#define OPENCV_3
#ifdef OPENCV_3
    #include <opencv2/videoio.hpp>
    #include <opencv2/photo.hpp>
#else
    #include <opencv2/core/core.hpp>
    #include <opencv2/photo/photo.hpp>
    #include <opencv2/imgproc/imgproc.hpp>
    #include <opencv2/highgui/highgui.hpp>
#endif
#include <deque>

using Mat = cv::Mat;
const int cv_sumtype = CV_16UC3;
using sumtype = int16_t;

class Buffer
{
protected:
    std::deque<Mat> frames;
    cv::VideoWriter & output;
    int sumSize;
    bool is_subtitle;
    Mat rollingSum;
    Mat beginFrame;
    const int minArea = 400;
    const int min_length = 15;
    const float radius = 4;
    static const int max_difference = 15;
    static const int min_difference = 50;
    const int dilation = 3;
    const int begin_row, end_row, begin_bw, end_bw, begin_col, end_col;
    
public:
    Buffer(cv::VideoWriter & _output, cv::Size frameSize) :
            output(_output),
            sumSize(0),
            is_subtitle(false),
            rollingSum(Mat::zeros(frameSize, cv_sumtype)),
            begin_row(3 * frameSize.height / 4),
            end_row(frameSize.height),
            begin_bw(frameSize.width / 4),
            end_bw(3 * frameSize.width / 4),
            begin_col(3 * begin_bw),
            end_col(3 * end_bw) {
    }
    
    ~Buffer() {
        for (Mat & f : frames) {
            output.write(f);
        }
    }
    
    template<char update>
    void updateSum(const Mat & frame) {
        for (int i=begin_row; i<end_row; i++) {
            const unsigned char * inr = frame.ptr<const unsigned char>(i);
            sumtype * outr = rollingSum.ptr<sumtype>(i);
            for (int j=begin_col; j<end_col; j++) {
                outr[j] += update * inr[j];
            }
        }
        sumSize += update;
    }
    
    bool conforms(int count) const {
        return count > minArea and 3 * count < 2 * (end_row - begin_row) * (end_bw - begin_bw);
    }
    
    template<typename A, typename B>
    static int diff(A a, B b) {
        return (a > b) ? (a - b) : (b - a);
    }
    
    template<int limit>
    inline bool conforms(const unsigned char * frameRow, const sumtype * sumRow, int j) const {
        const int mul_limit = sumSize * limit;
        return
            (diff(sumRow[j+0], sumSize * frameRow[j+0]) <= mul_limit) and
            (diff(sumRow[j+1], sumSize * frameRow[j+1]) <= mul_limit) and
            (diff(sumRow[j+2], sumSize * frameRow[j+2]) <= mul_limit) and
            true;
    }
    
    template <bool flip>
    inline void updateMask(const Mat & frame, Mat & result) const {
        for (int i=begin_row; i<end_row; i++) {
            const unsigned char * fr = frame.ptr<const unsigned char>(i);
            const sumtype * sr = rollingSum.ptr<sumtype>(i);
            unsigned char * outr = result.ptr<unsigned char>(i);
            for (int j=begin_bw, jj=begin_col; j<end_bw; j++, jj += 3) {
                if (flip ^ conforms<flip ? max_difference : min_difference>(fr, sr, jj)) {
                    outr[j] = 0;
                }
            }
        }
    }
    
    template <bool useEnd=false>
    inline Mat mask(const Mat & endFrame) {
        Mat result(rollingSum.size(), CV_8UC1);
        for (int i=0; i<rollingSum.rows; i++) {
            unsigned char * outr = result.ptr<unsigned char>(i);
            for (int j=0; j<rollingSum.cols; j++) {
                outr[j] = (i >= begin_row and i < end_row and j >= begin_bw and j < end_bw) ? 1 : 0;
            }
        }
        updateMask<false>(beginFrame, result);
        for (const Mat & frame : frames) {
            updateMask<true>(frame, result);
        }
        updateMask<not useEnd>(endFrame, result);
        return result;
    }
    
    void write_all(const Mat & endFrame) {
        Mat inpainted;
        Mat m = mask<true>(endFrame);
        cv::dilate(m, m, cv::Mat(), cv::Point(-1, -1), dilation);
        for (Mat & frame : frames) {
            cv::inpaint(frame, m, inpainted, radius, cv::INPAINT_TELEA);
            output.write(inpainted);
        }
        beginFrame = endFrame;
        frames.clear();
        rollingSum = Mat::zeros(rollingSum.size(), cv_sumtype);
        sumSize = 0;
    }
    
    void pop_front(bool write=true) {
        beginFrame = frames.front();
        if (write) {
            output.write(beginFrame);
        }
        updateSum<-1>(frames.front());
        frames.pop_front();
    }
    
    void push_back(Mat && f) {
        if (beginFrame.empty()) {
            beginFrame = f;
            output.write(f);
            return;
        }
        if (frames.size() >= min_length) {
            // NOTE: here, we should just update the mask and not process the whole buffer again
            if (is_subtitle and conforms(cv::countNonZero(mask<true>(f)))) {
                write_all(f);
                is_subtitle = false;
            } else if (is_subtitle) {
                Buffer tmp(output, f.size());
                while (frames.size() > min_length and not conforms(cv::countNonZero(mask<false>(f)))) {
                    tmp.push_back(frames.front().clone());
                    pop_front(false);
                    if (sumSize < min_length and frames.size() > sumSize) {
                        updateSum<+1>(frames[sumSize]);
                    }
                }
                if (frames.size() <= min_length) {
                    is_subtitle = false;
                }
            } else if (not is_subtitle and conforms(cv::countNonZero(mask<false>(f)))) {
                is_subtitle = true;
            }
        }
        frames.push_back(std::move(f));
        if (not is_subtitle and frames.size() > min_length) {
            pop_front();
        }
        if (sumSize < min_length and frames.size() > sumSize) {
            updateSum<+1>(frames[sumSize]);
        }
    }
};

int main(int argc, char * argv[])
{
    if (argc <= 1) {
        fprintf(stderr, "usage: subtitle_remover <filename> [output_name [seek_seconds [length_in_seconds]]]\n");
        return EXIT_FAILURE;
    }
    std::string inFileName(argv[1]);
    cv::VideoCapture video(inFileName);
    if (not video.isOpened()) {
        fprintf(stderr, "Cannot read from %s\n", argv[1]);
    }
    int length = 0;
    if (argc > 3) {
        int seek = std::atoi(argv[3]);
        video.set(cv::CAP_PROP_POS_MSEC, seek*1000);
        double msec = video.get(cv::CAP_PROP_POS_MSEC);
        printf("Seek to %i:%f\n", int(msec) / 60000, (int(msec) % 60000) / 1000.0);
    }
    if (argc > 4) {
        length = std::atoi(argv[4]);
    }
    int width = video.get(cv::CAP_PROP_FRAME_WIDTH);
    int height = video.get(cv::CAP_PROP_FRAME_HEIGHT);
    double fps = video.get(cv::CAP_PROP_FPS);
    int fourcc = video.get(cv::CAP_PROP_FOURCC);
    std::string outFileName = (argc > 2) ? argv[2] : std::string(argv[1], strrchr(argv[1], '.')) + "_nosub.avi";
    cv::VideoWriter output(outFileName, fourcc, fps, cv::Size(width, height));
    if (not output.isOpened()) {
        fprintf(stderr, "Cannot write to %s\n", outFileName.c_str());
        return EXIT_FAILURE;
    }

    printf("Writing to %s (%ix%i @ %g)\n", outFileName.c_str(), width, height, fps);
    Buffer buffer(output, cv::Size(width, height));
    Mat frame;
    for (int count=0; video.read(frame) and (not length or count < length); count++) {
        buffer.push_back(frame.clone());
    }
    return EXIT_SUCCESS;
}
