# Learning OS – AI Learning Copilot

## 1. Bằng chứng

### Nỗi đau

Sinh viên học AI/Data Science thường gặp khó khăn:

* Không biết nên học gì trước, học gì sau.
* Tài liệu quá nhiều và phân tán.
* Dễ bị "tutorial hell" (xem nhiều nhưng không làm được dự án).
* Khó chuyển kiến thức thành portfolio hoặc sản phẩm thực tế.

### Trải nghiệm trực tiếp

Nhóm đã tự trải nghiệm:

* Học LangChain, LangGraph, RAG thông qua YouTube, GitHub và blog.
* Mất nhiều giờ để tìm roadmap phù hợp.
* Thường xuyên bị lạc giữa nhiều khóa học và công nghệ khác nhau.
* Khó xác định bước tiếp theo để tiến tới một dự án hoàn chỉnh.

### Nguồn bên ngoài

#### Reddit

Nhiều bài đăng trong các cộng đồng AI/ML đề cập:

> "I don't know what to learn next."

> "There are too many resources and no clear roadmap."

#### Coursera Reviews

Người học đánh giá:

> Khóa học tốt nhưng thiếu hướng dẫn cá nhân hóa theo trình độ.

#### Giả định của nhóm

* Người học muốn có một AI mentor cá nhân.
* Người học sẵn sàng chia sẻ mục tiêu nghề nghiệp để nhận lộ trình phù hợp.

(Đây là giả định, chưa được kiểm chứng bằng phỏng vấn người dùng.)

---

## 2. Lát cắt để build

### Một người dùng

Sinh viên năm cuối ngành Data Science.

### Một công việc

Muốn học AI Engineering để xin việc.

### Một quyết định AI

AI xác định bước học tiếp theo dựa trên:

* Kỹ năng hiện tại
* Mục tiêu nghề nghiệp

### Một kết quả

AI sinh ra roadmap học tập cá nhân hóa gồm:

* Kỹ năng cần học
* Dự án cần làm
* Thời gian dự kiến

---

## 3. AI Product Canvas

### Value — Giá trị

#### Đối tượng

* Sinh viên CNTT
* Sinh viên Data Science
* Người chuyển ngành sang AI

#### Pain Point

* Không biết học gì tiếp theo.
* Bị quá tải bởi lượng tài liệu.

#### Giá trị AI

AI tạo roadmap cá nhân hóa thay vì dùng lộ trình chung cho tất cả mọi người.

---

### Trust — Niềm tin

Nếu AI đề xuất sai:

* Người dùng thấy lý do đề xuất.
* Có thể chỉnh sửa mục tiêu.
* Có thể yêu cầu tạo lại roadmap.
* Có nút feedback.

Người dùng luôn là người quyết định cuối cùng.

---

### Feasibility — Tính khả thi

#### Model

* GPT-4o-mini hoặc GPT-5-mini

#### Chi phí

* Thấp
* Mỗi lượt tạo roadmap chỉ cần vài nghìn token

#### Độ trễ

* Khoảng 2–5 giây

#### Dữ liệu

* Hồ sơ người học
* Kỹ năng hiện có
* Mục tiêu nghề nghiệp

#### Rủi ro lớn nhất

Roadmap không phù hợp với trình độ thực tế.

#### Điều kiện dừng

Nếu trên 50% người dùng đánh giá roadmap không hữu ích.

---

### Tín hiệu học

Thu thập:

* Người dùng sửa roadmap
* Người dùng bỏ qua gợi ý nào
* Người dùng đánh dấu hoàn thành bài học

Sử dụng dữ liệu này để:

* Tinh chỉnh prompt
* Điều chỉnh thứ tự học
* Cải thiện tập kiểm thử

---

## 4. Tăng năng lực hay tự động hóa

### Lựa chọn

Tăng năng lực (Augment)

### Vai trò AI

* Đề xuất
* Giải thích
* Lập kế hoạch

### Vai trò con người

* Chọn roadmap
* Chọn khóa học
* Quyết định học gì

### Lý do

Sai roadmap không gây hậu quả nghiêm trọng.

Người dùng có thể chỉnh sửa dễ dàng.

---

## 5. Bốn đường đi của trải nghiệm

### Đường thuận

AI tự tin.

Ví dụ:

Input:

"Tôi biết Python và SQL, muốn trở thành AI Engineer."

Output:

Roadmap 6 tháng.

Người dùng bấm:

"Chấp nhận roadmap"

---

### Khi AI không chắc

Ví dụ:

"Tôi muốn học AI."

AI hỏi thêm:

* Bạn đã biết Python chưa?
* Mục tiêu nghề nghiệp là gì?

---

### Khi AI sai

Ví dụ:

AI đề xuất học Deep Learning trước khi học Machine Learning.

Người dùng:

* Chỉnh sửa roadmap
* Tạo lại roadmap
* Gửi feedback

---

### Khi người dùng sửa

Ví dụ:

Người dùng kéo:

"Machine Learning"

lên trước

"Deep Learning"

Hệ thống lưu:

* Đề xuất ban đầu
* Đề xuất sau chỉnh sửa

để phân tích sau.

---

## 6. Những kiểu lỗi đáng lo nhất

### Lỗi 1 — Hallucination

Khi nào?

* AI tự tạo khóa học không tồn tại.

Hậu quả

* Người học mất thời gian.

Giảm thiểu

* Chỉ lấy khóa học từ danh sách đã xác thực.

---

### Lỗi 2 — Roadmap quá khó

Khi nào?

* Người mới nhưng AI đánh giá sai trình độ.

Hậu quả

* Người học bỏ cuộc.

Giảm thiểu

* Hỏi thêm câu đánh giá năng lực.

---

### Lỗi 3 — Thiếu thông tin

Khi nào?

* Người dùng nhập quá ngắn.

Ví dụ:

"Học AI"

Hậu quả

* Roadmap không phù hợp.

Giảm thiểu

* Bắt buộc hỏi thêm thông tin.

---

## 7. Kế hoạch kiểm thử và bằng chứng demo

### Test Case 1 (Đường thuận)

Input:

"Tôi biết Python, SQL và Pandas. Tôi muốn trở thành AI Engineer trong 6 tháng."

Kỳ vọng:

Roadmap rõ ràng, hợp lý.

---

### Test Case 2 (Khó)

Input:

"Tôi muốn học AI."

Kỳ vọng:

AI nhận biết thiếu dữ liệu và hỏi lại.

---

### Bằng chứng cần lưu

* Screenshot giao diện
* Prompt hệ thống
* Prompt người dùng
* Kết quả đầu ra
* Các trường hợp lỗi
* Quyết định thiết kế

---

## 8. Phân công

### Mã Vĩnh Lộc

* Prompt Engineering
* Evaluation
* Backend
* API
* Model Integration
* Thuyết trình

### Nguyễn Khánh Bằng

* Thu thập bằng chứng
* Test Cases
* Frontend UI
* Viết SPEC
* Demo Script
* Thuyết trình

---

# Demo Flow

1. Người dùng nhập kỹ năng hiện tại.
2. Người dùng nhập mục tiêu nghề nghiệp.
3. AI phân tích hồ sơ.
4. AI tạo roadmap cá nhân hóa.
5. Người dùng chỉnh sửa roadmap.
6. Hệ thống lưu feedback.
7. Demo cơ chế phục hồi khi AI không chắc.
