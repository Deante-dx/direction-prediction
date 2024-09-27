#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <Eigen/Dense>
#include <boost/math/special_functions/binomial.hpp>

using namespace std;
using namespace Eigen;

class BezierPredictor {
public:
    BezierPredictor(int h, int m, int n, double spe, double ang)
        : h(h), m(m), n(n), SPE(spe), ANG(ang) {}

    pair<Vector2d, int> predictDirection(vector<Vector2d>& H, vector<Vector2d>& B, Vector2d DIR) {
        if (H.size() < h) {
            cout << "Needs " << h - H.size() << " more points!" << endl;
            return {DIR, 1};
        } else if (H.size() > h) {
            H.erase(H.begin());
        }

        // 过滤B中的点
        H.erase(remove_if(H.begin(), H.end(), [&](const Vector2d& point) {
            return find(B.begin(), B.end(), point) != B.end();
        }), H.end());

        if (DIR.isZero()) {
            MatrixXd bezier_points = bezierCurve(H, m);
            DIR = calculateTangentDirection(bezier_points, 2);
        } else {
            auto [DIR_base, SPE_base] = calculate2PointsDirectionSpeed(H);
            double ANG_base = calculateAngle(DIR, DIR_base);

            if (ANG_base > ANG && SPE_base < SPE) {
                B.push_back(H.back());
            }
        }

        return {DIR, 0}; // 成功退出
    }

private:
    int h;      // 需要的轨迹点个数
    int m;      // 贝塞尔曲线上点的个数
    int n;      // 贝塞尔曲线上用于求DIR的点的个数
    double SPE; // 速度阈值
    double ANG; // 夹角阈值

    // 计算贝塞尔曲线
    MatrixXd bezierCurve(const vector<Vector2d>& points, int num_points) {
        int n = points.size() - 1;
        MatrixXd curve(num_points, 2);
        VectorXd t = VectorXd::LinSpaced(num_points, 0, 1);

        for (int i = 0; i <= n; ++i) {
            double coeff = boost::math::binomial_coefficient<double>(n, i);
            curve.rowwise() += coeff * (t.array().pow(i) * ((1 - t.array()).pow(n - i))).matrix().asDiagonal() * points[i].transpose();
        }

        return curve;
    }

    // 计算切线方向
    Vector2d calculateTangentDirection(const MatrixXd& bezier_points, int num_avg) {
        Vector2d last_point = bezier_points.row(bezier_points.rows() - 1);
        MatrixXd second_last_points = bezier_points.block(bezier_points.rows() - num_avg - 1, 0, num_avg, 2);
        
        Vector2d tangent_vector = last_point - second_last_points.colwise().mean();
        return tangent_vector.normalized(); // 单位向量
    }

    // 计算两个点的方向和速度
    pair<Vector2d, double> calculate2PointsDirectionSpeed(const vector<Vector2d>& points) {
        Vector2d vector = points.back() - points[points.size() - 2];
        double speed = vector.norm();
        if (speed == 0) {
            return {Vector2d(0, 0), 0};
        }
        return {vector.normalized(), speed}; // 单位向量
    }

    // 计算夹角
    double calculateAngle(const Vector2d& v1, const Vector2d& v2) {
        double norm_v1 = v1.norm();
        double norm_v2 = v2.norm();

        if (norm_v1 == 0 || norm_v2 == 0) {
            return 190.0;
        }

        double dot_product = v1.dot(v2);
        double cos_theta = std::clamp(dot_product / (norm_v1 * norm_v2), -1.0, 1.0);
        double angle_rad = acos(cos_theta);
        return angle_rad * (180.0 / M_PI); // 转换为角度
    }
};

int main() {
    vector<Vector2d> H = { {1, 2}, {2, 3}, {1, 2}, {2, 3}, {1, 2}, {2, 3}, {1, 2}, {2, 3}, {1, 2}, {2, 3} };
    vector<Vector2d> B;
    Vector2d DIR(0, 0);
    
    // 初始化参数
    int h = 10;
    int m = 5;
    int n = 2;
    double SPE = 0.05;
    double ANG = 90;

    // 创建贝塞尔预测器对象
    BezierPredictor predictor(h, m, n, SPE, ANG);
    auto result = predictor.predictDirection(H, B, DIR);

    cout << "Direction: (" << result.first.x() << ", " << result.first.y() << ")" << endl;

    return 0;
}
