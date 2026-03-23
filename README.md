
# Bài thuyết trình — 8 Use Case hệ thống Drivon

> Gợi ý: Điều chỉnh số slide (Slide X–Y) cho khớp bộ slide nhóm bạn.

## Mục lục (thứ tự thuyết trình gợi ý: 01 → 08)

| # | Use Case | Ghi chú |
|---|----------|---------|
| 01 | Register Account | Đăng ký + token email |
| 02 | Login / Logout | JWT, PasswordEncoder |
| 03 | Update Profile | PUT profile, trùng SĐT |
| 04 | Change Password | Đổi / tạo mật khẩu |
| 05 | Reset Forgotten Password | Mã 6 số, reset |
| 06 | View Profile | Nhiều API (image, withdraw) |
| 07 | Verify Email / Phone | Gắn signup; phone: backend chưa đủ |
| **08 ⭐** | **Manage Payment Methods** | **PayOS, cash, Payment** — **use case nghiệp vụ trọng tâm** |

> **Cách dùng file này:** Mỗi use case (01–08) đều có **đủ 5 phần**: **Activity Diagram**, **Sequence Diagram**, **Communication Diagram**, **State Diagram**, **Class Diagram** — mỗi phần gồm **câu mở đầu**, **chỉ vào sơ đồ**, **đi từng bước**, **câu chốt**. Khi lên lớp, em trình **01→08**; **UC08 ⭐** có thể để **cuối** hoặc **nhấn mạnh** như slide trọng tâm.

---

# USE CASE 01: REGISTER ACCOUNT — Đăng ký tài khoản

**Slide tương ứng:** *(điền)*

**Câu định hướng:**

✦ *"Thưa cô, **Register Account** là bước **đầu tiên** để người dùng vào hệ thống Drivon. Nhóm em **không** để mở tài khoản đầy đủ ngay — mà **tạo tài khoản chờ xác thực email**, gửi **mã 6 số**, và chỉ khi **verify** thì mới **kích hoạt** — để đảm bảo **email thật** và **giảm spam**."*

---

## 📊 1. ACTIVITY DIAGRAM

### ▌ CÂU MỞ ĐẦU

*"Activity Diagram mô tả luồng: **validate form** → **signup** → **kiểm tra email** → **lưu User + token** trong Database → **gửi email** → (sau đó) **verify** → **kích hoạt**."*

### ▌ CHỈ VÀO SƠ ĐỒ — Swimlane / partition

*"Nếu sơ đồ có **partition Database**, đó là các bước **persist User** và **EmailVerificationToken** — **không** để mã xác thực chỉ trong RAM."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** User mở **Register Page**, nhập email, password, họ tên, phone, địa chỉ (theo Signup).

**BƯỚC 2:** Client **validate** — nếu sai → hiển thị lỗi, **dừng**.

**BƯỚC 3:** **POST /auth/signup** — **UserService** kiểm tra **email đã tồn tại** — nếu có → **400** + lỗi.

### ✦ Lý do

*Không cho tạo **trùng email** — đảm bảo **một email một tài khoản**.*

**BƯỚC 4:** Tạo **User** trạng thái **PENDING_VERIFICATION**, **persist** User + **EmailVerificationToken** (6 số, hết hạn 5 phút), **EmailService** gửi mail.

**BƯỚC 5:** User nhập **mã verify** — **POST /auth/verify-email** — token hợp lệ → **update User** trong DB → **ACTIVE** → **Email verified successfully**.

### ▌ CÂU CHỐT

✦ *"Toàn bộ quy trình **đăng ký** và **lưu token** được **gắn với Database** — không phụ thuộc vào thao tác tay của admin."*

---

## 📊 2. SEQUENCE DIAGRAM

### ▌ CÂU MỞ ĐẦU

*"Sequence cho thấy **AuthController** nhận request, **UserService** xử lý nghiệp vụ, **UserRepository** và **EmailVerificationTokenRepository** gọi **MySQL**."*

### ▌ CHỈ VÀO SƠ ĐỒ — Các participant

*"**AuthController** — **UserService** — **UserRepository** — **EmailVerificationTokenRepository** — **EmailService** — **Database** (MySQL). **UserService** là tầng nghiệp vụ nên **không** có trên Communication diagram nếu nhóm chỉ vẽ Controller → Repository — khi đó em giải thích **UserService** nằm trong **AuthController** hoặc gộp theo diagram thực tế."*

### ▌ ĐI TỪNG BƯỚC — Luồng signup

**BƯỚC 1:** User / FE gửi **POST /auth/signup** tới **AuthController**.

**BƯỚC 2:** **AuthController** gọi **UserService.registerUser(SignupRequest)**.

**BƯỚC 3:** **UserService** gọi **UserRepository.findByEmail** — **UserRepository** truy vấn **MySQL** — trả `User | null`.

**BƯỚC 4:** Nếu email **đã tồn tại** → **UserService** báo lỗi → **AuthController** trả **400** → FE hiển thị lỗi — **dừng** nhánh thành công.

**BƯỚC 5:** Nếu email **chưa có** → **UserService** gọi **UserRepository.save(User)** — **persist** vào **MySQL**.

**BƯỚC 6:** **UserService** gọi **EmailVerificationTokenRepository.save(token)** — **persist** token vào **MySQL**.

**BƯỚC 7:** **UserService** gọi **EmailService.sendVerificationEmail(email, code)**.

**BƯỚC 8:** **UserService** trả kết quả cho **AuthController** — **AuthController** trả **201** — FE báo user kiểm tra email.

### ▌ ĐI TỪNG BƯỚC — Luồng verify email

**BƯỚC 1:** User nhập mã — FE gửi **POST /auth/verify-email**.

**BƯỚC 2:** **AuthController** gọi **UserService.verifyEmail** (hoặc logic tương đương).

**BƯỚC 3:** **UserService** gọi **TokenRepository.findByToken** / **findByUser** — truy vấn **MySQL**.

**BƯỚC 4:** Nếu token **không hợp lệ** → trả **400** — **dừng**.

**BƯỚC 5:** Nếu **hợp lệ** → **UserRepository.save(User)** cập nhật **status ACTIVE** — **EmailVerificationTokenRepository.delete(token)**.

**BƯỚC 6:** **AuthController** trả **200** — FE hiển thị **Email verified successfully**.

### ▌ CÂU CHỐT

✦ *"Controller **ủy quyền** cho **UserService** — đổi rule verify chỉ cần sửa **Service**."*

---

## 📊 3. COMMUNICATION DIAGRAM — Giao tiếp (đánh số)

### ▌ CÂU MỞ ĐẦU

*"Communication Diagram thể hiện **thứ tự message** giữa các **đối tượng** trên sơ đồ: User, SignupPage, AuthController, UserService, UserRepository, EmailVerificationTokenRepository, EmailService, MySQL. Em đọc theo số **1, 2, 3, 4, 4.1…** như trên slide."*

### ▌ CHỈ VÀO SƠ ĐỒ — Cấu trúc

*"Các **rectangle** là **đối tượng** (object); **actor** là User. Mũi tên có **thứ tự** — không chỉ “ai nói với ai” mà còn **thứ tự thực hiện**."*

### ▌ ĐI TỪNG BƯỚC (luồng đăng ký)

**BƯỚC 1:** User → SignupPage: mở trang, nhập dữ liệu đăng ký.

**BƯỚC 2:** SignupPage → AuthController: `POST /auth/signup`.

**BƯỚC 3:** AuthController → UserService: `registerUser()`.

**BƯỚC 4:** UserService → UserRepository: `findByEmail(email)`.

**BƯỚC 4.1:** UserRepository → MySQL: truy vấn user theo email.

**BƯỚC 4.2:** MySQL → UserRepository: trả về `user` hoặc `null`.

**BƯỚC 5:** UserService → UserRepository: `save(newUser)` (khi email chưa tồn tại).

**BƯỚC 5.1–5.3:** UserRepository ↔ MySQL: persist user, xác nhận đã lưu.

**BƯỚC 6:** UserService → EmailVerificationTokenRepository: `save(token)` (mã 6 số, hết hạn).

**BƯỚC 6.1–6.3:** TokenRepository ↔ MySQL: persist token.

**BƯỚC 7:** UserService → EmailService: gửi email xác thực.

**BƯỚC 8:** UserService → AuthController: `AuthResponse` / kết quả xử lý.

**BƯỚC 9:** AuthController → SignupPage: `201 Created` (hoặc lỗi).

**BƯỚC 10:** SignupPage → User: thông báo kiểm tra email / verify tài khoản.

### ▌ ĐI TỪNG BƯỚC (luồng xác thực email — nếu slide tách riêng)

*"Sau khi user nhập mã 6 số, các message tiếp tục: SignupPage → AuthController `POST /auth/verify-email` → UserService → UserRepository / TokenRepository → MySQL → cập nhật User (active) → xóa token → trả **200** cho FE."*

### ▌ CÂU CHỐT

✦ *"Communication Diagram **đánh số** giúp thầy cô thấy **chuỗi gọi** từ UI → Controller → Service → Repository → Database — **không** nhảy cóc từ form thẳng vào DB."*

---

## 📊 4. STATE DIAGRAM — Trạng thái

### ▌ CÂU MỞ ĐẦU

*"State Diagram mô tả **vòng đời tài khoản** và **trạng thái xác thực**: từ chưa có tài khoản đến đang chờ email, đã verify, đang hoạt động, hoặc các trạng thái phụ."*

### ▌ CHỈ VÀO SƠ ĐỒ — Các trạng thái và chuyển

*"Có **các ô trạng thái** (state) và **mũi tên chuyển** gắn nhãn sự kiện (ví dụ: đăng ký thành công, verify thành công, token hết hạn, admin khóa tài khoản)."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1: NoAccount** — Người dùng chưa đăng ký; chưa có bản ghi User trong hệ thống (theo context của sơ đồ).

**BƯỚC 2: PendingVerification** — Sau `POST /auth/signup` thành công: user đã được tạo nhưng **chưa** kích hoạt đầy đủ; có thể có **WaitingForEmailVerification** như trạng thái con trong cùng giai đoạn chờ mã.

**BƯỚC 3: Verified** — Mã email đúng, hợp lệ (trong thời hạn): **emailVerified** chuyển sang đúng.

**BƯỚC 4: Active** — Tài khoản **active**, user có thể đăng nhập và sử dụng đầy đủ chức năng (sau khi verify hoặc theo luồng mà nhóm đặt trên sơ đồ).

**BƯỚC 5 — Trạng thái phụ:** **Expired** — token hết hạn, user cần nhập lại mã hoặc gửi lại; **Suspended** — admin khóa; **Deleted** — kết thúc vòng đời tài khoản (nếu trên sơ đồ có nhánh này).

### ▌ CÂU CHỐT

✦ *"State Diagram **không** thay thế Activity — mà cho thấy **tài khoản có thể ở đâu** trong một thời điểm, và **sự kiện nào** đổi trạng thái."*

---

## 📊 5. CLASS DIAGRAM — Cấu trúc lớp

### ▌ CÂU MỞ ĐẦU

*"Class Diagram cố định **lớp nào** phụ thuộc **lớp nào**: **AuthController** nhận request, **UserService** chứa nghiệp vụ đăng ký và verify, **Repository** truy cập **User** và **EmailVerificationToken** — **Database** là tầng lưu trữ."*

### ▌ CHỈ VÀO SƠ ĐỒ — Các lớp và quan hệ

*"**AuthController** liên kết tới **UserService**. **UserService** liên kết **UserRepository**, **EmailVerificationTokenRepository**, **EmailService**. **UserRepository** và **EmailVerificationTokenRepository** truy cập **Database** (hoặc biểu diễn quan hệ **Repository → Database**). **User** và **EmailVerificationToken** là entity; **SignupRequest** / **AuthResponse** là DTO (nếu nhóm vẽ trên sơ đồ)."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** **AuthController** chỉ điều phối HTTP: không gọi trực tiếp SQL — gọi **UserService**.

**BƯỚC 2:** **UserService** thực hiện: kiểm tra trùng email, tạo user, tạo token, gọi gửi mail, verify token — **tập trung nghiệp vụ**.

**BƯỚC 3:** **UserRepository** thao tác CRUD trên **User**; **EmailVerificationTokenRepository** thao tác trên **EmailVerificationToken**.

**BƯỚC 4:** **EmailVerificationToken** thường **tham chiếu** hoặc **gắn** với **User** (một user một token đang hiệu lực theo thiết kế).

**BƯỚC 5:** **Database** (MySQL) là nơi **persist** — không có lưu mật khẩu dạng thô trong diagram (nếu có thì đã hash).

### ▌ CÂU CHỐT

✦ *"Tách **Controller / Service / Repository** giúp **đổi** cách gửi email hoặc **đổi** thời hạn token mà **không** phải sửa toàn bộ tầng HTTP."*

---

---

# USE CASE 02: LOGIN / LOGOUT — Đăng nhập / Đăng xuất

**Câu định hướng:**

✦ *"Sau khi có tài khoản, **Login** là **cổng bảo mật**: hệ thống **không** tin mật khẩu thô — mà **so khớp đã hash** bằng **PasswordEncoder**, cấp **JWT** bằng **JwtTokenProvider**; **Logout** thì **xóa phiên** và **ngắt WebSocket**."*

---

## 📊 1. ACTIVITY DIAGRAM

### ▌ CÂU MỞ ĐẦU

*"Thưa cô, Activity Diagram của **Login / Logout** mô tả **hai cụm**: **đăng nhập** (validate → gọi API → kiểm tra DB → JWT → lưu phiên) và **đăng xuất** (gọi logout → xóa phiên → ngắt WebSocket). Em đi theo mũi tên trên sơ đồ."*

### ▌ CHỈ VÀO SƠ ĐỒ — Cấu trúc

*"Nếu sơ đồ có **partition Database**, đó là bước **findByEmail** — đọc user từ MySQL. **Không** có nhánh “đăng nhập thành công” mà không qua kiểm tra password."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** Input không hợp lệ → chỉ báo lỗi, không gọi server.

**BƯỚC 2:** User không tồn tại hoặc sai password → **400** + toast.

**BƯỚC 3:** Đúng → **AuthResponse** + lưu token và user.

### ▌ CÂU CHỐT

✦ *"JWT **không** lưu mật khẩu — chỉ **định danh phiên** sau khi password đã đúng."*

---

## 📊 2. SEQUENCE DIAGRAM

### ▌ CÂU MỞ ĐẦU

*"Sequence Diagram cho thấy **thứ tự theo thời gian**: Frontend gửi credentials, **AuthController** điều phối, **UserRepository** đọc DB, **PasswordEncoder** so khớp hash, **JwtTokenProvider** sinh JWT — từ trên xuống dưới."*

### ▌ CHỈ VÀO SƠ ĐỒ — Các participant

*"**LoginPage** (Web Browser) — **AuthController** — **UserRepository** — **PasswordEncoder** — **JwtTokenProvider** — **MySQL**. Mỗi cột là một **lifeline**; activation bar (nếu có) là lúc đối tượng đang xử lý."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** **POST /auth/login** → **findByEmail**.

**BƯỚC 2:** **PasswordEncoder.matches** — sai → **400**.

**BƯỚC 3:** **createToken** → **200 AuthResponse** → FE lưu **localStorage** + **WebSocket**.

**BƯỚC 4: Logout:** **POST /auth/logout** → xóa token, user, **disconnect WebSocket**, redirect **/auth**.

### ▌ CÂU CHỐT

✦ *"Tách **PasswordEncoder** và **JwtTokenProvider** — **đổi thuật toán hash** hoặc **thời hạn JWT** không làm vỡ toàn bộ controller."*

---

## 📊 3. COMMUNICATION DIAGRAM — Giao tiếp (đánh số)

### ▌ CÂU MỞ ĐẦU

*"Communication Diagram dùng **message đánh số phân cấp** (1, 2, 2.1, 2.2, 2.3…) để thầy cô đọc đúng **thứ tự** khi demo."*

### ▌ CHỈ VÀO SƠ ĐỒ

*"**User** tương tác **LoginPage**; **LoginPage** gửi request tới **AuthController**; **AuthController** phối hợp **UserRepository**, **PasswordEncoder**, **JwtTokenProvider**; **UserRepository** trao đổi với **MySQL**."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** User → LoginPage: chọn Login, nhập email và password.

**BƯỚC 2:** LoginPage → AuthController: `POST /auth/login` (submit credentials).

**BƯỚC 2.1:** AuthController → UserRepository: `findByEmail(email)`.

**BƯỚC 2.1.1:** UserRepository → MySQL: truy vấn bản ghi User.

**BƯỚC 2.1.2:** MySQL → UserRepository: trả `User` hoặc rỗng.

**BƯỚC 2.1.3:** UserRepository → AuthController: kết quả tìm user.

**BƯỚC 2.2:** AuthController → PasswordEncoder: `matches(rawPassword, encodedPassword)`.

**BƯỚC 2.2.1:** PasswordEncoder → AuthController: `true` hoặc `false`.

**BƯỚC 2.3:** AuthController → JwtTokenProvider: `createToken(email)` (khi password đúng).

**BƯỚC 2.3.1:** JwtTokenProvider → AuthController: chuỗi JWT.

**BƯỚC 3:** AuthController → LoginPage: `AuthResponse` hoặc thông báo lỗi (400).

**BƯỚC 4:** LoginPage → User: lưu token/user vào localStorage, chuyển trang; hoặc hiển thị lỗi.

**BƯỚC 5 (Logout):** User → LoginPage: click Logout.

**BƯỚC 5.1:** LoginPage → AuthController: `POST /auth/logout`.

**BƯỚC 5.2:** AuthController → LoginPage: phản hồi thành công (ví dụ 200).

**BƯỚC 5.3:** LoginPage → User: xóa localStorage, ngắt WebSocket, redirect `/auth`.

### ▌ CÂU CHỐT

✦ *"Thứ tự **2.1 → 2.2 → 2.3** nhấn mạnh: **có user** rồi mới **so password**, rồi mới **cấp JWT** — không đảo ngược."*

---

## 📊 4. STATE DIAGRAM — Trạng thái

### ▌ CÂU MỞ ĐẦU

*"State Diagram mô tả **phiên đăng nhập**: đã logout, đang gửi đăng nhập, đã đăng nhập, hoặc đăng nhập thất bại."*

### ▌ CHỈ VÀO SƠ ĐỒ

*"Trạng thái ban đầu thường là **LoggedOut**. Chuyển sang **LoggingIn** khi user submit. **LoggedIn** khi nhận JWT và lưu phiên. Quay **LoggedOut** khi logout hoặc token hết hạn (401)."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1: LoggedOut** — Chưa có phiên hợp lệ trong app (hoặc đã xóa).

**BƯỚC 2: LoggingIn** — Đã gửi `POST /auth/login`, đang chờ phản hồi.

**BƯỚC 3: LoggedIn** — Đã lưu JWT và thông tin user; có thể kết nối WebSocket.

**BƯỚC 4: LoginFailed** — Sai mật khẩu hoặc không tìm thấy user; có thể retry → quay **LoggedOut** hoặc vẫn ở form login.

**BƯỚC 5:** Từ **LoggedIn**, sự kiện **Logout** hoặc **Token Expired / 401** → **LoggedOut**.

### ▌ CÂU CHỐT

✦ *"**LoggedIn** không phải trạng thái vĩnh viễn — luôn có đường về **LoggedOut** để đảm bảo **an toàn phiên**."*

---

## 📊 5. CLASS DIAGRAM — Cấu trúc lớp

### ▌ CÂU MỞ ĐẦU

*"Class Diagram thể hiện **AuthController** phụ thuộc **UserRepository**, **PasswordEncoder**, **JwtTokenProvider**; DTO **LoginRequest**, **AuthResponse**; entity **User**."*

### ▌ CHỈ VÀO SƠ ĐỒ

*"**AuthController** không chứa thuật toán hash — gọi **PasswordEncoder**. **JwtTokenProvider** tách riêng **sinh token**. **UserRepository** là cổng truy cập **User** trong Database."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** **AuthController** nhận `LoginRequest`, trả `AuthResponse` (chứa JWT và thông tin user nếu thiết kế như vậy).

**BƯỚC 2:** **UserRepository** cung cấp `findByEmail` — map với bảng User trên MySQL.

**BƯỚC 3:** **PasswordEncoder** (Spring Security) — `encode`, `matches`.

**BƯỚC 4:** **JwtTokenProvider** — tạo JWT từ email/username sau khi xác thực.

**BƯỚC 5:** **User** có các trường như `email`, `password` (hash), `status` — tùy sơ đồ nhóm.

### ▌ CÂU CHỐT

✦ *"Tách **JwtTokenProvider** giúp **đổi thời hạn token** hoặc **claims** mà không trộn vào **AuthController**."*

---

---

# USE CASE 03: UPDATE PROFILE — Cập nhật hồ sơ

**Câu định hướng:**

✦ *"Khi người dùng **đổi thông tin liên hệ** (họ tên, SĐT, địa chỉ, avatar), hệ thống phải **đảm bảo SĐT không trùng** với user khác và **đồng bộ** lại **localStorage** sau khi server trả user đã lưu."*

---

## 📊 1. ACTIVITY DIAGRAM

### ▌ CÂU MỞ ĐẦU

*"Thưa cô, Activity Diagram **Update Profile** mô tả từ lúc user mở trang hồ sơ, chỉnh sửa, đến khi **PUT** lên server và **cập nhật** dữ liệu trong MySQL — rồi **đồng bộ** lại giao diện và localStorage."*

### ▌ CHỈ VÀO SƠ ĐỒ — Cấu trúc

*"Sơ đồ có **nhánh điều kiện**: validate client; user có tồn tại không; **phone** có bị trùng không. **Partition Database** gắn với **findByEmail**, **findByPhone**, **save**."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** Validate client (fullName bắt buộc, phone 10 số).

**BƯỚC 2:** User không tồn tại → **404**.

**BƯỚC 3:** **Phone** đã dùng bởi người khác → **400**.

**BƯỚC 4:** OK → **persist User** → **200** → **onUpdateUser** + localStorage.

### **Nhánh avatar** (nếu slide có):

*"**PUT /profile/update-avatar** — chỉ cập nhật **avatarUrl**."*

### ▌ CÂU CHỐT

✦ *"Kiểm tra **findByPhone** trước khi save — tránh **hai tài khoản cùng một số**."*

---

## 📊 2. SEQUENCE DIAGRAM

### ▌ CÂU MỞ ĐẦU

*"Sequence Diagram cho thấy **ProfileController** nhận **PUT /profile/update**, gọi **UserRepository** theo thứ tự: tìm user theo email → (nếu đổi SĐT) tìm theo phone → **save** — và phản hồi **200** cùng user đã lưu."*

### ▌ CHỈ VÀO SƠ ĐỒ — Các participant

*"**ProfilePage** (Frontend) — **ProfileController** — **UserRepository** — **MySQL**. Nhánh **update-avatar** (nếu có trên slide) tương tự: **PUT /profile/update-avatar**."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** **PUT /profile/update** → **findByEmail**.

**BƯỚC 2:** Nếu đổi phone → **findByPhone** → conflict → **400**.

**BƯỚC 3:** **save** → **200 saved User** → FE cập nhật state.

### ▌ CÂU CHỐT

✦ *"**ProfileController** chỉ điều phối; **quy tắc trùng SĐT** nằm tập trung ở một chỗ — tránh hai user dùng chung một số điện thoại."*

---

## 📊 3. COMMUNICATION DIAGRAM — Giao tiếp (đánh số)

### ▌ CÂU MỞ ĐẦU

*"Communication Diagram dùng **message có số thứ tự** giữa User, ProfilePage, ProfileController, UserRepository, MySQL — đúng với file `communication.puml` của nhóm."*

### ▌ CHỈ VÀO SƠ ĐỒ

*"User kích hoạt **Save**; ProfilePage gửi **PUT**; Controller trao đổi với Repository nhiều lần (find email, find phone, save)."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** User → ProfilePage: chỉnh sửa profile, bấm Save.

**BƯỚC 2:** ProfilePage → ProfileController: `PUT /profile/update` (body chứa email và các trường cập nhật).

**BƯỚC 3:** ProfileController → UserRepository: `findByEmail(email)`.

**BƯỚC 3.1:** UserRepository → MySQL: truy vấn user theo email.

**BƯỚC 3.2:** MySQL → UserRepository: trả user hoặc null.

**BƯỚC 4:** UserRepository → ProfileController: kết quả **user / empty**.

**BƯỚC 5:** ProfileController → UserRepository: `findByPhone(newPhone)` — **chỉ khi** user đổi số điện thoại.

**BƯỚC 5.1–5.2:** UserRepository ↔ MySQL: kiểm tra phone đã tồn tại.

**BƯỚC 6:** UserRepository → ProfileController: đã có người dùng phone đó hoặc không.

**BƯỚC 7:** ProfileController → UserRepository: `save(updatedUser)`.

**BƯỚC 7.1–7.2:** UserRepository ↔ MySQL: persist user.

**BƯỚC 8:** UserRepository → ProfileController: user đã lưu.

**BƯỚC 9:** ProfileController → ProfilePage: `200` + JSON user hoặc mã lỗi (404/400).

**BƯỚC 10:** ProfilePage → User: cập nhật UI, toast thành công, cập nhật localStorage.

### ▌ CÂU CHỐT

✦ *"Số thứ tự **3→5→7** nhấn mạnh: **tìm user** → **kiểm tra phone** → **mới save** — không save mù quáng."*

---

## 📊 4. STATE DIAGRAM — Trạng thái

### ▌ CÂU MỞ ĐẦU

*"State Diagram mô tả **trạng thái màn hồ sơ**: đang xem, đang sửa, đang lưu, hoặc lưu thất bại."*

### ▌ CHỈ VÀO SƠ ĐỒ

*"**ViewingProfile** là trạng thái mặc định khi đang xem thông tin. **EditingProfile** khi bấm Edit. **Saving** khi đã gửi request cập nhật."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1: ViewingProfile** — Đang xem thông tin đã load (từ localStorage + API nếu có).

**BƯỚC 2:** User bấm **Edit** → chuyển **EditingProfile**.

**BƯỚC 3:** Validation phía client thất bại → **ValidationFailed** → user sửa lại → quay **EditingProfile**.

**BƯỚC 4:** User bấm **Save** → **Saving** — đang chờ phản hồi server.

**BƯỚC 5:** Thành công → quay **ViewingProfile** (dữ liệu mới).

**BƯỚC 6:** Lỗi server hoặc conflict (ví dụ phone trùng) → **SaveFailed** → user chỉnh lại hoặc thử lại → **EditingProfile**.

**BƯỚC 7:** User có thể thoát khỏi màn hồ sơ từ **ViewingProfile** (kết thúc luồng trên sơ đồ nếu có nút kết thúc).

### ▌ CÂU CHỐT

✦ *"**Saving** là trạng thái **tạm** — luôn phải quay về **ViewingProfile** hoặc **EditingProfile**, không “kẹt” mãi ở đang lưu."*

---

## 📊 5. CLASS DIAGRAM — Cấu trúc lớp

### ▌ CÂU MỞ ĐẦU

*"Class Diagram: **ProfileController** cung cấp API cập nhật hồ sơ và avatar; **UserRepository** truy cập entity **User**; **Database** lưu trữ."*

### ▌ CHỈ VÀO SƠ ĐỒ

*"Các phương thức tiêu biểu: `updateProfile`, `updateAvatar`, `checkPasswordStatus` (nếu nhóm vẽ). **User** chứa `fullName`, `phone`, `address`, `avatarUrl`, …"*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** **ProfileController** phụ thuộc **UserRepository** để đọc/ghi **User**.

**BƯỚC 2:** **UserRepository** phụ thuộc **Database** (MySQL) — `findByEmail`, `findByPhone`, `save`.

**BƯỚC 3:** **User** là entity JPA (hoặc model persistence) — một dòng trong bảng user.

**BƯỚC 4:** Frontend **ProfilePage** (nếu vẽ ở tầng UI) gọi REST tới **ProfileController** — quan hệ phụ thuộc **uses** hoặc **dependency**.

**BƯỚC 5:** **Separation of concerns**: không nhét logic trùng SĐT vào entity **User** — đặt ở tầng controller/service tùy kiến trúc nhóm.

### ▌ CÂU CHỐT

✦ *"**UserRepository** tái sử dụng cho nhiều use case — **Update Profile** chỉ là một **consumer** của các hàm find/save."*

---

---

# USE CASE 04: CHANGE PASSWORD — Đổi / Tạo mật khẩu

**Câu định hướng:**

✦ *"Use Case này **phục vụ hai nhóm**: user **đã có mật khẩu** (đổi mật khẩu có **mật khẩu cũ**), và user **đăng nhập Google** **chưa có mật khẩu** (tạo mật khẩu mới). Em dùng **GET check-password-status** để **giao diện đúng form**."*

---

## 📊 1. ACTIVITY DIAGRAM

### ▌ CÂU MỞ ĐẦU

*"Thưa cô, Activity Diagram **Change Password** có **hai nhánh nghiệp vụ**: user **đã có mật khẩu** (đổi có nhập mật khẩu cũ) và user **chưa có mật khẩu** (Google-only — **tạo mật khẩu**). Nhánh nào cũng **ghi DB** sau khi encode."*

### ▌ CHỈ VÀO SƠ ĐỒ — Cấu trúc

*"Điểm rẽ nhánh đầu tiên thường là kết quả **GET check-password-status**. **Partition Database** đi kèm các bước **findByEmail**, **persist** password đã hash."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** **GET /profile/check-password-status/{email}** → **findByEmail** → `{ hasPassword }`.

**BƯỚC 2:** **Change password** → **matches** mật khẩu cũ — sai → **401**.

**BƯỚC 3:** **Encode** mật khẩu mới → **save**.

**BƯỚC 4:** **Create password** — nếu user đã có password → **400**; nếu chưa → **encode + save**.

### ▌ CÂU CHỐT

✦ *"Không có **mật khẩu cũ** thì **không** cho đổi kiểu ‘đổi mật khẩu’ — để tránh **khai thác** đường đổi mật khẩu."*

---

## 📊 2. SEQUENCE DIAGRAM

### ▌ CÂU MỞ ĐẦU

*"Sequence Diagram cho thấy **FE** gọi **check-password-status** trước; sau đó **change-password** hoặc **create-password** — **ProfileController** dùng **PasswordEncoder** và **UserRepository**."*

### ▌ CHỈ VÀO SƠ ĐỒ — Các participant

*"**ChangePasswordPage** — **ProfileController** — **UserRepository** — **PasswordEncoder** — **MySQL**. Thời gian chạy **từ trên xuống**."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** **checkPasswordStatus** → **findByEmail**.

**BƯỚC 2:** **change-password** → **matches** → **save** encoded.

**BƯỚC 3:** **create-password** → encode + save.

### ▌ CÂU CHỐT

✦ *"Mật khẩu **không** lưu thô — chỉ **hash** qua **PasswordEncoder**."*

---

## 📊 3. COMMUNICATION DIAGRAM — Giao tiếp (đánh số)

### ▌ CÂU MỞ ĐẦU

*"Communication Diagram đánh số message giữa **ChangePasswordPage**, **ProfileController**, **UserRepository**, **PasswordEncoder**, **MySQL** — khớp sơ đồ giao tiếp của nhóm."*

### ▌ CHỈ VÀO SƠ ĐỒ

*"Luồng bắt đầu bằng **checkPasswordStatus** để biết hiển thị form nào; sau đó user nhập và **submit**."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** ChangePasswordPage → ProfileController: `GET` hoặc gọi API **check-password-status** (theo thiết kế URL trên slide).

**BƯỚC 2:** ProfileController → UserRepository: `findByEmail(email)`.

**BƯỚC 2.1:** UserRepository → MySQL: truy vấn user.

**BƯỚC 2.2:** MySQL → UserRepository: bản ghi user.

**BƯỚC 3:** UserRepository → ProfileController: dữ liệu user.

**BƯỚC 4:** ProfileController → ChangePasswordPage: `{ hasPassword: true/false }`.

**BƯỚC 5:** User → ChangePasswordPage: nhập mật khẩu (cũ/mới hoặc chỉ mới tùy nhánh).

**BƯỚC 6:** ChangePasswordPage → ProfileController: submit **change-password** hoặc **create-password**.

**BƯỚC 7:** ProfileController → UserRepository: `findByEmail` lần nữa trước khi đổi.

**BƯỚC 7.1–7.2:** UserRepository ↔ MySQL: lấy user hiện tại.

**BƯỚC 8:** UserRepository → ProfileController: user.

**BƯỚC 9:** ProfileController → PasswordEncoder: **verify** (nhánh đổi mật khẩu) — `matches(plain, hash)`.

**BƯỚC 10:** PasswordEncoder → ProfileController: hợp lệ / không hợp lệ.

**BƯỚC 11:** ProfileController → UserRepository: **save** user với `password` đã **encode** (mới).

**BƯỚC 11.1–11.2:** UserRepository ↔ MySQL: cập nhật bản ghi.

**BƯỚC 13:** ProfileController → ChangePasswordPage: phản hồi thành công (ví dụ 200).

**BƯỚC 14:** ChangePasswordPage → User: toast / redirect (ví dụ về `/profile`).

### ▌ CÂU CHỐT

✦ *"Bước **9–10** là “**chốt an toàn**”: không encode mật khẩu mới nếu **mật khẩu cũ** sai (nhánh đổi mật khẩu)."*

---

## 📊 4. STATE DIAGRAM — Trạng thái

### ▌ CÂU MỞ ĐẦU

*"State Diagram phản ánh **trạng thái giao diện** sau khi biết user **đã có hay chưa có mật khẩu**, và các bước **đang đổi / đang tạo / lỗi**."*

### ▌ CHỈ VÀO SƠ ĐỒ

*"**Unknown** trước khi gọi check-password-status. **HasPassword** vs **NoPassword** là hai vùng trạng thái chính."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1: Unknown** — Chưa biết user thuộc nhánh nào; đang chờ **check-password-status**.

**BƯỚC 2:** `hasPassword = true` → **HasPassword** — hiển thị form **đổi mật khẩu** (có mật khẩu hiện tại).

**BƯỚC 3:** `hasPassword = false` → **NoPassword** — hiển thị form **tạo mật khẩu**.

**BƯỚC 4:** Từ **HasPassword**, submit **change-password** → **Changing** — đang xử lý.

**BƯỚC 5:** Thành công → quay **HasPassword** (mật khẩu mới đã lưu); hoặc **ChangeFailed** (401, sai mật khẩu cũ) → user sửa lại → **HasPassword**.

**BƯỚC 6:** Từ **NoPassword**, submit **create-password** → **Creating**.

**BƯỚC 7:** Thành công → chuyển **HasPassword** (giờ user đã có mật khẩu cục bộ trên server).

**BƯỚC 8:** **CreateFailed** — ví dụ user đã có mật khẩu (400) → quay **NoPassword** để thử lại.

### ▌ CÂU CHỐT

✦ *"Hai vùng **HasPassword** và **NoPassword** tương ứng **hai API khác nhau** — không gộp một form cho cả hai."*

---

## 📊 5. CLASS DIAGRAM — Cấu trúc lớp

### ▌ CÂU MỞ ĐẦU

*"Class Diagram: **ChangePasswordPage** (UI) phụ thuộc **ProfileController** qua REST; **ProfileController** dùng **UserRepository** và **PasswordEncoder**; **User** chứa `email`, `password` (hash)."*

### ▌ CHỈ VÀO SƠ ĐỒ

*"**ProfileController** có các method: `checkPasswordStatus`, `changePassword`, `createPassword`. **PasswordEncoder** là bean bảo mật của Spring — không phải entity."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** **ChangePasswordPage** — thuộc tính: mật khẩu hiện tại, mật khẩu mới, xác nhận, cờ `hasPassword`; phương thức `handleSubmit`.

**BƯỚC 2:** **ProfileController** — nhận `Map` hoặc DTO request, trả `ResponseEntity`.

**BƯỚC 3:** **UserRepository** — `findByEmail`, `save`.

**BƯỚC 4:** **PasswordEncoder** — `encode`, `matches`.

**BƯỚC 5:** **User** — một dòng user trong DB; trường password luôn là **hash**.

### ▌ CÂU CHỐT

✦ *"**PasswordEncoder** tách khỏi **User** — đúng nguyên tắc: entity **không** tự hash mật khẩu trong diagram nghiệp vụ chuẩn."*

---

---

# USE CASE 05: RESET FORGOTTEN PASSWORD — Quên mật khẩu

**Câu định hướng:**

✦ *"Khi user **quên mật khẩu**, hệ thống **không** gửi mật khẩu mới qua email — mà gửi **mã 6 số có hạn**, **xác minh** rồi **đặt lại** mật khẩu mới và **xóa token** — tránh **token tái sử dụng**."*

---

## 📊 1. ACTIVITY DIAGRAM

### ▌ CÂU MỞ ĐẦU

*"Thưa cô, Activity Diagram **Reset Forgotten Password** chia **ba giai đoạn**: gửi **mã 6 số** qua email, **xác minh mã**, rồi **đặt lại mật khẩu** và **xóa token** — mỗi giai đoạn đều **chạm Database** (User, PasswordResetToken)."*

### ▌ CHỈ VÀO SƠ ĐỒ — Cấu trúc

*"Có **điều kiện** email có tồn tại không; **điều kiện** mã đúng/sai/hết hạn. **Partition Database** gắn với persist token, xóa token, cập nhật password user."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1: Gửi mã:** **POST /auth/send-reset-code** — nếu email **không** có user vẫn cấu trúc **response chung** (không tiết lộ tồn tại email) — nếu có → **xóa token cũ**, **lưu token mới** (5 phút), **gửi email**.

### ✦ Lý do

*Không cho attacker biết **email nào** đã đăng ký.*

**BƯỚC 2: Verify:** **POST /auth/verify-reset-code** — so khớp mã, kiểm tra **hết hạn**.

**BƯỚC 3: Reset:** **POST /auth/reset-password** — **encode** mật khẩu mới → **save User** → **delete token** → redirect **/auth**.

### ▌ CÂU CHỐT

✦ *"Token **một lần** — xóa sau reset — giảm **rủi ro** mã bị lộ."*

---

## 📊 2. SEQUENCE DIAGRAM

### ▌ CÂU MỞ ĐẦU

*"Sequence Diagram cho thấy **AuthController** nhận **ba endpoint** khác nhau; **PasswordResetTokenRepository** quản lý **token có thời hạn**; **EmailService** gửi mã; **PasswordEncoder** chỉ dùng ở bước **reset-password** (encode mật khẩu mới)."*

### ▌ CHỈ VÀO SƠ ĐỒ — Các participant

*"**ForgotPasswordPage** — **AuthController** — **UserRepository** — **PasswordResetTokenRepository** — **EmailService** — **PasswordEncoder** — **MySQL**."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** **send-reset-code** → find user → delete + save token → send email.

**BƯỚC 2:** **verify-reset-code** → find token → validate.

**BƯỚC 3:** **reset-password** → encode → save user → **delete token**.

### ▌ CÂU CHỐT

✦ *"**AuthController** điều phối **ba** endpoint; **Repository** tách **User** và **PasswordResetToken** — đúng **Single Responsibility**."*

---

## 📊 3. COMMUNICATION DIAGRAM — Giao tiếp (đánh số)

### ▌ CÂU MỞ ĐẦU

*"Communication Diagram chia **ba đoạn message**: **1→8** gửi mã; **9→13** xác minh mã; **14→21** đặt lại mật khẩu và xóa token — thầy cô có thể theo dõi **từng đoạn** khi demo."*

### ▌ CHỈ VÀO SƠ ĐỒ

*"**ForgotPasswordPage** — **AuthController** — **UserRepository** — **PasswordResetTokenRepository** — **EmailService** — **PasswordEncoder** — **MySQL**."*

### ▌ ĐI TỪNG BƯỚC — Đoạn gửi mã (1–8)

**BƯỚC 1:** User → ForgotPasswordPage: nhập email, yêu cầu gửi mã.

**BƯỚC 2:** ForgotPasswordPage → AuthController: `POST /auth/send-reset-code`.

**BƯỚC 3:** AuthController → UserRepository: `findByEmail`.

**BƯỚC 3.1:** UserRepository → MySQL: truy vấn user.

**BƯỚC 3.2:** MySQL → UserRepository: user hoặc null.

**BƯỚC 4:** UserRepository → AuthController: kết quả.

**BƯỚC 5:** AuthController → PasswordResetTokenRepository: xóa token cũ (nếu có).

**BƯỚC 5.1:** TokenRepository → MySQL: delete.

**BƯỚC 6:** AuthController → PasswordResetTokenRepository: **save** mã mới (6 số, hết hạn).

**BƯỚC 6.1–6.2:** TokenRepository ↔ MySQL: persist token.

**BƯỚC 7:** AuthController → EmailService: gửi email chứa mã.

**BƯỚC 8:** AuthController → ForgotPasswordPage: OK (và thông báo chung nếu email không tồn tại — theo thiết kế).

### ▌ ĐI TỪNG BƯỚC — Đoạn xác minh (9–13)

**BƯỚC 9:** User → ForgotPasswordPage: nhập mã.

**BƯỚC 10:** ForgotPasswordPage → AuthController: `POST /auth/verify-reset-code`.

**BƯỚC 11:** AuthController → PasswordResetTokenRepository: `find` token theo user.

**BƯỚC 11.1–11.2:** TokenRepository ↔ MySQL: đọc token.

**BƯỚC 12:** PasswordResetTokenRepository → AuthController: token hoặc null.

**BƯỚC 13:** AuthController → ForgotPasswordPage: OK hoặc lỗi (sai mã / hết hạn).

### ▌ ĐI TỪNG BƯỚC — Đoạn reset (14–21)

**BƯỚC 14:** User → ForgotPasswordPage: nhập mật khẩu mới + xác nhận.

**BƯỚC 15:** ForgotPasswordPage → AuthController: `POST /auth/reset-password`.

**BƯỚC 16:** AuthController → PasswordEncoder: `encode(newPassword)`.

**BƯỚC 17:** PasswordEncoder → AuthController: chuỗi hash.

**BƯỚC 18:** AuthController → UserRepository: `save` user với password mới.

**BƯỚC 18.1–18.2:** UserRepository ↔ MySQL: persist user.

**BƯỚC 19:** AuthController → PasswordResetTokenRepository: **delete** token.

**BƯỚC 19.1:** TokenRepository → MySQL: xóa token.

**BƯỚC 20:** AuthController → ForgotPasswordPage: thành công.

**BƯỚC 21:** ForgotPasswordPage → User: toast, redirect `/auth`.

### ▌ CÂU CHỐT

✦ *"Ba đoạn **1–8**, **9–13**, **14–21** tương ứng **ba** API — dễ **đối chiếu** với code và với slide."*

---

## 📊 4. STATE DIAGRAM — Trạng thái

### ▌ CÂU MỞ ĐẦU

*"State Diagram mô tả **vòng đời quên mật khẩu**: từ trạng thái nghỉ, đến đã gửi mã, đang xác minh, đã hợp lệ mã, đang đặt lại mật khẩu, hoàn tất."*

### ▌ CHỈ VÀO SƠ ĐỒ

*"Các trạng thái như **Idle**, **CodeRequested**, **CodeSent**, **VerifyingCode**, **CodeValid**, **ResettingPassword**, **Completed** — tùy nhãn chính xác trên slide nhóm."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1: Idle** — User chưa bắt đầu hoặc đang ở màn nhập email.

**BƯỚC 2:** User gửi email → **CodeRequested** — hệ thống chuẩn bị tạo token.

**BƯỚC 3:** Token lưu DB + email gửi → **CodeSent** — user có thể nhập mã.

**BƯỚC 4:** User gửi mã → **VerifyingCode** — đang kiểm tra.

**BƯỚC 5:** Mã đúng, chưa hết hạn → **CodeValid** — cho phép bước nhập mật khẩu mới.

**BƯỚC 6:** Mã sai hoặc hết hạn → **CodeInvalid** — có thể resend / thử lại → quay **CodeSent**.

**BƯỚC 7:** Từ **CodeValid**, user submit mật khẩu mới → **ResettingPassword**.

**BƯỚC 8:** Cập nhật DB + xóa token → **Completed** — kết thúc use case.

**BƯỚC 9:** Lỗi server khi reset → **ResetFailed** — retry → quay **CodeValid**.

### ▌ CÂU CHỐT

✦ *"Trạng thái **CodeValid** là “**cửa**” để vào **ResettingPassword** — không cho reset nếu **chưa** verify mã."*

---

## 📊 5. CLASS DIAGRAM — Cấu trúc lớp

### ▌ CÂU MỞ ĐẦU

*"Class Diagram: **AuthController** phối hợp **UserRepository**, **PasswordResetTokenRepository**, **EmailService**, **PasswordEncoder**; entity **PasswordResetToken** gắn với **User**."*

### ▌ CHỈ VÀO SƠ ĐỒ

*"**PasswordResetToken** có `token`, `expiryDate`, `user`, phương thức `isExpired()` nếu nhóm vẽ."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** **AuthController** — `sendResetCode`, `verifyResetCode`, `resetPassword`.

**BƯỚC 2:** **UserRepository** — `findByEmail`, `save`.

**BƯỚC 3:** **PasswordResetTokenRepository** — `findByUser`, `save`, `delete`.

**BƯỚC 4:** **EmailService** — `sendPasswordResetCode(email, code)`.

**BƯỚC 5:** **PasswordEncoder** — `encode` (dùng khi reset mật khẩu).

**BƯỚC 6:** **User** — `email`, `password` (hash), …

**BƯỚC 7:** **PasswordResetToken** — quan hệ tới **User**; **Database** lưu cả hai bảng.

### ▌ CÂU CHỐT

✦ *"Tách **PasswordResetToken** thành entity/bảng riêng — **không** nhét mã reset vào bảng User — dễ **đặt hạn** và **xóa** sau dùng."*

---

---

# USE CASE 06: VIEW PROFILE — Xem hồ sơ

**Câu định hướng:**

✦ *"**View Profile** không chỉ **hiển thị** thông tin cá nhân — mà **gộp** từ **localStorage** (phiên đăng nhập) và **nhiều API**: **trạng thái mật khẩu**, **giấy tờ** (UserImage), **yêu cầu rút tiền** (OwnerWithdraw) — để **một màn** đủ thông tin cho người dùng."*

---

## 📊 1. ACTIVITY DIAGRAM

### ▌ CÂU MỞ ĐẦU

*"Thưa cô, Activity Diagram **View Profile** mô tả **đọc dữ liệu**: kiểm tra phiên local, rồi **gọi song song hoặc tuần tự** các API để ghép **một màn hồ sơ đầy đủ** — không chỉ thông tin user mà còn **giấy tờ** và **rút tiền**."*

### ▌ CHỈ VÀO SƠ ĐỒ — Cấu trúc

*"Nhánh **đầu tiên** thường là **có user trong localStorage không** — không thì **redirect /auth**. Các bước sau **partition Database** cho từng API đọc DB."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** Kiểm tra **đăng nhập** (localStorage).

**BƯỚC 2:** Tải **hasPassword** + **danh sách ảnh giấy tờ** + **danh sách withdraw**.

**BƯỚC 3:** **Render** UI (personal info, security, documents, withdraw requests).

### ▌ CÂU CHỐT

✦ *"**Tách biệt** controller: **Profile** không chứa hết **image** và **withdraw** — mỗi **bounded context** một API."*

---

## 📊 2. SEQUENCE DIAGRAM

### ▌ CÂU MỞ ĐẦU

*"Sequence Diagram cho thấy **một màn profile** hợp nhất **ba nguồn**: trạng thái mật khẩu (**ProfileController**), danh sách ảnh giấy tờ (**UserImageController**), yêu cầu rút tiền (**OwnerWithdrawController**) — tất cả đọc từ **MySQL**."*

### ▌ CHỈ VÀO SƠ ĐỒ — Các participant

*"**ProfilePage** — **localStorage** — **ProfileController** — **UserImageController** — **OwnerWithdrawController** — **MySQL**. **localStorage** không phải server nhưng là **participant** lưu phiên client."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** **getItem('user')** — không có → redirect.

**BƯỚC 2:** **check-password-status** → **findByEmail**.

**BƯỚC 3:** **GET /user/image** → query **UserImage**.

**BƯỚC 4:** **GET /owner-withdraw/{userId}** → query **OwnerWithdrawRequest**.

### ▌ CÂU CHỐT

✦ *"Đây là **read-heavy** use case — không đổi dữ liệu trong luồng chính; đảm bảo **đồng bộ** nhiều nguồn trên **một UI**."*

---

## 📊 3. COMMUNICATION DIAGRAM — Giao tiếp (đánh số)

### ▌ CÂU MỞ ĐẦU

*"Communication Diagram đánh số từ **1 đến 10**: từ **navigate** tới **render** — thầy cô thấy rõ **localStorage** đứng trước **các API**."*

### ▌ CHỈ VÀO SƠ ĐỒ

*"**User** — **ProfilePage** — **LocalStorage** — **ProfileController** — **UserImageController** — **OwnerWithdrawController** — **MySQL**."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** User → ProfilePage: điều hướng tới `/profile`.

**BƯỚC 2:** ProfilePage → LocalStorage: `getItem('user')`.

**BƯỚC 3:** LocalStorage → ProfilePage: chuỗi JSON user hoặc `null`.

**BƯỚC 4:** ProfilePage → ProfileController: gọi **check-password-status** (kèm email từ user).

**BƯỚC 4.1:** ProfileController → MySQL: truy vấn user (qua tầng repository trên sơ đồ có thể gộp thành “query user”).

**BƯỚC 4.2:** MySQL → ProfileController: dữ liệu phục vụ tính `hasPassword`.

**BƯỚC 5:** ProfileController → ProfilePage: `{ hasPassword }` hoặc tương đương.

**BƯỚC 6:** ProfilePage → UserImageController: `GET /user/image?userId=...`.

**BƯỚC 6.1–6.2:** UserImageController ↔ MySQL: truy vấn **UserImage**.

**BƯỚC 7:** UserImageController → ProfilePage: danh sách ảnh / giấy tờ.

**BƯỚC 8:** ProfilePage → OwnerWithdrawController: `GET /owner-withdraw/{userId}`.

**BƯỚC 8.1–8.2:** OwnerWithdrawController ↔ MySQL: truy vấn **OwnerWithdrawRequest**.

**BƯỚC 9:** OwnerWithdrawController → ProfilePage: danh sách yêu cầu rút tiền.

**BƯỚC 10:** ProfilePage → User: render giao diện hoặc **redirect /auth** nếu không có user.

### ▌ CÂU CHỐT

✦ *"Bước **2–3** là **cổng bảo vệ**: không gọi API profile nếu **chưa đăng nhập** (không có user trong storage)."*

---

## 📊 4. STATE DIAGRAM — Trạng thái

### ▌ CÂU MỞ ĐẦU

*"State Diagram mô tả **trạng thái màn profile**: chưa load, đang kiểm tra đăng nhập, đang tải dữ liệu, đã load, lỗi, hoặc bị redirect."*

### ▌ CHỈ VÀO SƠ ĐỒ

*"Trạng thái đầu **NotLoaded** hoặc tương đương; có nhánh **Redirected** khi không có user."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1: NotLoaded** — Chưa bắt đầu hoặc component vừa mount.

**BƯỚC 2:** User mở `/profile` → **CheckingAuth** — đọc localStorage.

**BƯỚC 3:** Không có user → **Redirected** → kết thúc luồng xem profile (chuyển `/auth`).

**BƯỚC 4:** Có user → **LoadingData** — đang gọi các API (password status, image, withdraw).

**BƯỚC 5:** API lỗi → **LoadFailed** — có thể retry → quay **LoadingData**.

**BƯỚC 6:** Đủ dữ liệu → **Loaded** — hiển thị đầy đủ các khối UI.

**BƯỚC 7:** Từ **Loaded**, user bấm **Edit** (nếu cùng màn hoặc chuyển màn) → **Editing** — khi xong cancel/save có thể quay **Loaded** (theo sơ đồ nhóm).

**BƯỚC 8:** Từ **Loaded** hoặc **Redirected** có thể thoát → kết thúc (nếu có nút terminal trên sơ đồ).

### ▌ CÂU CHỐT

✦ *"**LoadingData** và **Loaded** tách rõ **đang chờ** và **đã hiển thị** — tránh UI nhấp nháy khi chưa có dữ liệu."*

---

## 📊 5. CLASS DIAGRAM — Cấu trúc lớp

### ▌ CÂU MỞ ĐẦU

*"Class Diagram: **ProfilePage** phụ thuộc **ba controller** REST; mỗi controller truy cập **Database** qua repository tương ứng; entity **UserImage**, **OwnerWithdrawRequest**."*

### ▌ CHỈ VÀO SƠ ĐỒ

*"**ProfilePage** có state: `user`, `editedUser`, `userImages`, `withdrawRequests`, `hasPassword`; method `fetchUserImages`, `checkPasswordStatus` — theo diagram nhóm."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** **ProfilePage** — tầng presentation — gọi API qua HTTP client.

**BƯỚC 2:** **ProfileController** — `checkPasswordStatus(email)` — đọc user/security.

**BƯỚC 3:** **UserImageController** — `list(userId)` — trả về **UserImage** (ảnh, loại giấy tờ, trạng thái verify nếu có).

**BƯỚC 4:** **OwnerWithdrawController** — `getByOwner(ownerId)` — trả **OwnerWithdrawRequest**.

**BƯỚC 5:** Cả ba controller **truy cập Database** (trên sơ đồ có thể gộp hoặc tách **Repository**).

**BƯỚC 6:** **UserImage** — thuộc tính `imageId`, `imageUrl`, `documentType`, `verified`, …

**BƯỚC 7:** **OwnerWithdrawRequest** — `requestId`, `amount`, `status`, `sign`, …

### ▌ CÂU CHỐT

✦ *"**Một trang** — **ba controller** — phản ánh **tách module** backend: profile / KYC image / withdraw **không** nhét chung một endpoint “siêu lớn”."*

---

---

# USE CASE 07: VERIFY EMAIL / PHONE — Xác thực email (và số điện thoại)

**Câu định hướng:**

✦ *"Use Case này **gắn chặt** với **đăng ký** và **bảo mật**: sau signup, user **inactive** và **emailVerified=false**; chỉ khi **mã 6 số** đúng **trong hạn** thì **kích hoạt** — đồng thời **JWT + login ngay** để **không bắt** user đăng nhập lại. Em lưu ý: **phần verify phone** chưa có endpoint riêng trong backend — nhóm **ghi rõ** trong diagram/ báo cáo."*

---

## 📊 1. ACTIVITY DIAGRAM

### ▌ CÂU MỞ ĐẦU

*"Thưa cô, Activity Diagram **Verify Email** (gắn với **đăng ký**) mô tả: **signup** → lưu user **inactive** + token → gửi mail → user nhập mã → **verify-email** → **kích hoạt** user → **xóa token** → **JWT** → **tự động đăng nhập**. Có nhánh **resend** và nhánh **trùng email/phone**."*

### ▌ CHỈ VÀO SƠ ĐỒ — Cấu trúc

*"**Partition Database** bao quanh **persist User**, **persist token**, **update User**, **delete token**. Nhánh lỗi: trùng email/phone; mã sai; mã hết hạn."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** **existsByEmail / existsByPhone** — trùng → **400**.

**BƯỚC 2:** Lưu **inactive user** + token **5 phút** + **gửi email**.

**BƯỚC 3:** **verify-email** — đúng → **active** + **JWT**; sai → **400**; có thể **resend**.

### ▌ CÂU CHỐT

✦ *"**Xóa token** sau khi verify — tránh **dùng lại** cùng mã."*

---

## 📊 2. SEQUENCE DIAGRAM

### ▌ CÂU MỞ ĐẦU

*"Sequence Diagram cho thấy **AuthController** điều phối **signup**, **verify-email**, **resend-verification**; **JwtTokenProvider** chỉ xuất hiện **sau** khi verify thành công — cấp JWT để **auto login**."*

### ▌ CHỈ VÀO SƠ ĐỒ — Các participant

*"**SignupPage** — **AuthController** — **UserRepository** — **EmailVerificationTokenRepository** — **EmailService** — **JwtTokenProvider** — **MySQL**."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** **signup** → save user + token + send email.

**BƯỚC 2:** **verify-email** → find user + token → save → delete token → **createToken** → **AuthResponse**.

**BƯỚC 3:** **resend-verification** → delete token cũ + token mới + send email.

### ▌ CÂU CHỐT

✦ *"**JwtTokenProvider** chỉ chạy **sau** khi email **đã verified** — đúng nghiệp vụ **kích hoạt**; không cấp JWT cho user **inactive**."*

---

## 📊 3. COMMUNICATION DIAGRAM — Giao tiếp (đánh số)

### ▌ CÂU MỞ ĐẦU

*"Communication Diagram chia **hai giai đoạn message**: **1→7** đăng ký và gửi token; **8→17** nhập mã, kích hoạt user, xóa token, cấp JWT — đúng thứ tự trên sơ đồ nhóm."*

### ▌ CHỈ VÀO SƠ ĐỒ

*"**User** — **SignupPage** — **AuthController** — **UserRepository** — **EmailVerificationTokenRepository** — **EmailService** — **JwtTokenProvider** — **MySQL**."*

### ▌ ĐI TỪNG BƯỚC — Đoạn signup (1–7)

**BƯỚC 1:** User → SignupPage: submit form đăng ký.

**BƯỚC 2:** SignupPage → AuthController: `POST /auth/signup`.

**BƯỚC 3:** AuthController → UserRepository: `existsByEmail` / `existsByPhone` (hoặc tương đương).

**BƯỚC 3.1:** UserRepository → MySQL: kiểm tra trùng.

**BƯỚC 3.2:** MySQL → UserRepository: kết quả.

**BƯỚC 4:** AuthController → UserRepository: `save` user **inactive**, `emailVerified = false`.

**BƯỚC 4.1–4.2:** UserRepository ↔ MySQL: persist user.

**BƯỚC 5:** AuthController → EmailVerificationTokenRepository: `save` token (6 số, 5 phút).

**BƯỚC 5.1–5.2:** TokenRepository ↔ MySQL: persist token.

**BƯỚC 6:** AuthController → EmailService: gửi email chứa mã.

**BƯỚC 7:** AuthController → SignupPage: thông báo thành công (kiểm tra email).

### ▌ ĐI TỪNG BƯỚC — Đoạn verify + JWT (8–17)

**BƯỚC 8:** User → SignupPage: nhập mã 6 số.

**BƯỚC 9:** SignupPage → AuthController: `POST /auth/verify-email`.

**BƯỚC 10:** AuthController → UserRepository: `findByEmail`.

**BƯỚC 10.1–10.2:** UserRepository ↔ MySQL: lấy user.

**BƯỚC 11:** AuthController → EmailVerificationTokenRepository: `findByUser` / tìm token.

**BƯỚC 11.1–11.2:** TokenRepository ↔ MySQL: đọc token.

**BƯỚC 12:** AuthController → UserRepository: `save` user — `emailVerified = true`, `status = active`.

**BƯỚC 12.1–12.2:** UserRepository ↔ MySQL: persist.

**BƯỚC 13:** AuthController → EmailVerificationTokenRepository: `delete` token.

**BƯỚC 13.1:** TokenRepository → MySQL: xóa token.

**BƯỚC 14:** AuthController → JwtTokenProvider: `createToken(email)`.

**BƯỚC 15:** JwtTokenProvider → AuthController: JWT.

**BƯỚC 16:** AuthController → SignupPage: `AuthResponse` (JWT + user).

**BƯỚC 17:** SignupPage → User: lưu phiên — **đã đăng nhập** (auto login).

### ▌ ĐI TỪNG BƯỚC — Resend (nếu slide có)

*"User bấm **Resend** → `POST /auth/resend-verification` → xóa token cũ → tạo token mới → gửi lại email — message tiếp theo trên sơ đồ nhóm."*

### ▌ CÂU CHỐT

✦ *"Đoạn **8→17** là **chốt bảo mật**: chỉ sau **verify** mới có **JWT** — đúng story **kích hoạt tài khoản**."*

---

## 📊 4. STATE DIAGRAM — Trạng thái

### ▌ CÂU MỞ ĐẦU

*"State Diagram mô tả **trạng thái xác thực email** sau signup: **chưa verify**, **đã gửi mã**, **đang nhập mã**, **đã verify** hoặc **mã sai / hết hạn**."*

### ▌ CHỈ VÀO SƠ ĐỒ

*"**Unverified** (user.status = inactive). **CodeSent** sau khi có token và email đã gửi. **Verifying** khi user gửi mã."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1: Unverified** — Sau signup: user tồn tại nhưng **chưa** kích hoạt đầy đủ; `emailVerified=false`.

**BƯỚC 2:** Hệ thống sinh mã và gửi mail → **CodeSent** — user có thể nhập mã.

**BƯỚC 3:** User gửi mã → **Verifying** — đang kiểm tra.

**BƯỚC 4:** Mã đúng, chưa hết hạn → **Verified** — `emailVerified=true`, `status=active` (theo diagram).

**BƯỚC 5:** Từ **Verified** có thể chuyển tới trạng thái **đã đăng nhập** trên app (nếu sơ đồ gộp) hoặc kết thúc nhánh xác thực.

**BƯỚC 6:** **InvalidCode** — sai mã → có thể **resend** hoặc nhập lại → quay **CodeSent**.

**BƯỚC 7:** **ExpiredCode** — token hết hạn → **resend** → quay **CodeSent**.

### ▌ Ghi chú về Phone

*"Trên báo cáo nhóm em **ghi rõ**: **verify phone** riêng **chưa** có endpoint đầy đủ trong backend — chỉ có **existsByPhone** / `phone` trong signup nếu có."*

### ▌ CÂU CHỐT

✦ *"Hai nhánh **InvalidCode** và **ExpiredCode** đều quay về **CodeSent** — user **không bị kẹt** vĩnh viễn ở lỗi."*

---

## 📊 5. CLASS DIAGRAM — Cấu trúc lớp

### ▌ CÂU MỞ ĐẦU

*"Class Diagram: **AuthController** phối hợp **UserRepository**, **EmailVerificationTokenRepository**, **EmailService**, **JwtTokenProvider**; DTO **SignupRequest**; entity **User**; enum **UserStatus**; **EmailVerificationToken**."*

### ▌ CHỈ VÀO SƠ ĐỒ

*"**User** liên kết **UserStatus** (inactive / active / banned). **EmailVerificationToken** liên kết **User**; có `expires`, `isExpired()` nếu nhóm vẽ."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** **AuthController** — `signup`, `verifyEmail`, `resendVerification`.

**BƯỚC 2:** **SignupRequest** — `fullName`, `email`, `password`, `phone`, `address`.

**BƯỚC 3:** **UserRepository** — `existsByEmail`, `existsByPhone`, `findByEmail`, `save`.

**BƯỚC 4:** **EmailVerificationTokenRepository** — `findByUser`, `save`, `delete`.

**BƯỚC 5:** **EmailService** — `sendVerificationEmail(email, code)`.

**BƯỚC 6:** **JwtTokenProvider** — `createToken(email)` — cấp JWT sau verify.

**BƯỚC 7:** **User** — `email`, `phone`, `emailVerified`, `status`.

**BƯỚC 8:** **EmailVerificationToken** — `token`, `expiryDate`, `user`.

**BƯỚC 9:** **Database** — lưu **users** và **email_verification_tokens** (tên bảng theo JPA).

### ▌ CÂU CHỐT

✦ *"**JwtTokenProvider** đứng **cạnh** AuthController trong diagram — **không** nằm trong **User** — vì JWT là **dịch vụ phiên**, không phải cột DB."*

---

---
# USE CASE 08 ⭐: MANAGE PAYMENT METHODS — Quản lý phương thức thanh toán (Thuê xe)

**Slide tương ứng:** *(điền: Slide …–…)*

**Câu định hướng (nói trước khi vào Use Case này):**

✦ *"Thưa cô, **Manage Payment Methods** là Use Case ⭐ trọng tâm của nhóm em trong luồng nghiệp vụ thuê xe. Sau khi người dùng chọn xe và đặt cọc, hệ thống cần **tạo giao dịch thanh toán rõ ràng** — chuyển khoản qua **PayOS** hoặc **tiền mặt** — và **lưu trữ trạng thái** từng lần thanh toán trong MySQL, để đảm bảo minh bạch giữa khách, chủ xe và chủ hệ thống."*

---

## 📊 1. ACTIVITY DIAGRAM — Sơ đồ hoạt động

### ▌ CÂU MỞ ĐẦU KHI TRÌNH BÀY

*"Thưa cô, đây là Activity Diagram mô tả toàn bộ quy trình từ lúc người dùng **chọn phương thức thanh toán** cho đến khi **bản ghi Payment** được lưu vào Database — và có nhánh **cập nhật** sau thanh toán. Em sẽ đi theo luồng mũi tên trên sơ đồ."*

### ▌ CHỈ VÀO SƠ ĐỒ — Cấu trúc tổng quan

*"Đầu tiên, cô để ý sơ đồ có **partition Database** (hoặc các nhánh ghi DB): đó là nơi **Payment** được **persist** sau khi tạo link — để trạng thái **PENDING** không chỉ nằm trên giao diện mà **có bản ghi thật** trong MySQL."*

*"Luồng chính **rẽ nhánh** theo hai loại: **bank (PayOS)** và **cash (tiền mặt)** — hai cách hoàn thành thanh toán khác nhau nhưng **cùng một mô hình** lưu `Payment`."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1: Bắt đầu booking / payment**

*"Người dùng bắt đầu luồng thanh toán từ màn **thực hiện đặt xe / thanh toán** (ví dụ RentalForm, MyRentals). Đây là điểm khởi đầu của Activity."*

### ✦ Lý do thiết kế

*Mỗi lần thanh toán gắn với **một bản ghi Payment** — không gộp chung “tài khoản” thanh toán toàn cục; phù hợp mô hình **đặt cọc theo từng đơn**.*

---

**BƯỚC 2: Chọn phương thức — Bank**

*"Nếu người dùng chọn **ngân hàng / PayOS**, hệ thống gọi **POST /api/payments/create**. Backend **tạo link thanh toán** qua PayOS, **lưu Payment** với `status = PENDING` và `method = bank`, sau đó **redirect** người dùng sang **PayOS checkout**."*

### ✦ Lý do thiết kế

*Lưu **PENDING** trước khi PayOS xác nhận — nếu user đóng tab, vẫn còn dấu vết trong DB để tra cứu.*

---

**BƯỚC 3: PayOS thành công (webhook / xác nhận)**

*"Khi PayOS báo **thành công** (webhook hoặc luồng xác nhận trên frontend), hệ thống cập nhật **Payment status = PAID** trong Database — đây là bước **đóng vòng** giao dịch ngân hàng."*

---

**BƯỚC 4: Chọn phương thức — Cash**

*"Nếu chọn **tiền mặt**, hệ thống gọi **POST /api/payments/cash**, **lưu Payment** `PENDING` với `method = cash`. Sau đó chủ xe / admin **hoàn tất** thu tiền mặt; có thể **cập nhật** trạng thái trong DB."*

---

**BƯỚC 5: Cập nhật bản ghi (nếu cần)**

*"Khi cần đổi **method** hoặc **status** cho một payment đã có, luồng dùng **PUT /api/payments/update/{paymentId}** — **query** rồi **persist** lại bản ghi trong Database."*

---

### ▌ CÂU CHỐT

✦ *"Activity Diagram này cho thấy: **mọi phương thức** đều đi qua **một lớp lưu trữ thống nhất** (Payment), và **Database** luôn tham gia ở các bước **tạo / cập nhật** sau thanh toán."*

---

## 📊 2. SEQUENCE DIAGRAM — Sơ đồ trình tự

### ▌ CÂU MỞ ĐẦU

*"Activity Diagram cho **cái gì** xảy ra; Sequence Diagram cho **ai làm việc với ai**, **theo thứ tự thời gian** — từ trên xuống dưới."*

### ▌ CHỈ VÀO SƠ ĐỒ — Các participant

*"Cô để ý các cột chính:
→ **PaymentController** — cổng REST `/api/payments`.
→ **PaymentService** — nghiệp vụ: tạo link PayOS, tạo cash payment, cập nhật.
→ **PaymentRepository** — truy cập **MySQL**.
→ **PayOS** — hệ thống thanh toán bên ngoài (bank)."*

---

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1: Bank — tạo thanh toán**

*"Frontend gửi **POST /payments/create** (PaymentRequest). **PaymentController** gọi **PaymentService.createPaymentRequest**. **Service** gọi **PayOS.createPaymentLink** nhận **checkoutUrl**; sau đó **PaymentRepository.save** — **persist** Payment vào DB **PENDING, bank**. Controller trả **200** kèm `checkoutUrl`, user được **redirect** sang PayOS."*

### ✦ Nguyên lý Single Responsibility

*Controller **không** đặt logic PayOS; **Service** gọi PayOS + save — dễ **đổi nhà cung cấp** hoặc rule sau này.*

---

**BƯỚC 2: Cash**

*"Frontend gửi **POST /payments/cash**. **PaymentService.createCashPayment** → **save** Payment **PENDING, cash** — không qua PayOS."*

---

**BƯỚC 3: Update**

*"Frontend gửi **PUT /payments/update/{paymentId}**. **Service** **findByPaymentId** → **save** bản ghi đã chỉnh sửa → **persist** DB."*

---

### ▌ CÂU CHỐT

✦ *"Tách **PaymentController** và **PaymentService** giúp nhóm em thay đổi **tích hợp PayOS** hoặc **quy tắc cập nhật** mà không phải sửa toàn bộ tầng API."*

---

## 📊 3. COMMUNICATION DIAGRAM — Giao tiếp (đánh số)

### ▌ CÂU MỞ ĐẦU

*"Communication Diagram nhấn mạnh **message có thứ tự** (1, 2, 3, 4…) giữa **PaymentView** (hoặc RentalForm / MyRentals), **PaymentController**, **PaymentService**, **PayOS**, **PaymentRepository**, **MySQL**. Em đọc **từng số** như trên slide."*

### ▌ CHỈ VÀO SƠ ĐỒ — Cấu trúc

*"User chọn **cash** hoặc **bank** — nhánh **bank** có thêm **PayOS**; **PaymentRepository** luôn **chạm MySQL** khi **save** hoặc **find**."*

### ▌ ĐI TỪNG BƯỚC — Tạo payment (thường là 1–10)

**BƯỚC 1:** User → PaymentView: chọn phương thức thanh toán (cash / bank).

**BƯỚC 2:** PaymentView → PaymentController: `POST /payments/create` **hoặc** `POST /payments/cash` (tùy nhánh).

**BƯỚC 3:** PaymentController → PaymentService: `createPaymentRequest` **hoặc** `createCashPayment`.

**BƯỚC 4 (nhánh bank):** PaymentService → PayOS: `createPaymentLink` / tạo link thanh toán.

**BƯỚC 5:** PayOS → PaymentService: trả **checkoutUrl** và dữ liệu link (theo SDK PayOS).

**BƯỚC 6:** PaymentService → PaymentRepository: `save(Payment)` với `status = PENDING`, `paymentMethod` = bank hoặc cash.

**BƯỚC 6.1:** PaymentRepository → MySQL: **persist** bản ghi Payment.

**BƯỚC 6.2:** MySQL → PaymentRepository: xác nhận đã lưu.

**BƯỚC 7:** PaymentRepository → PaymentService: **Payment** đã lưu.

**BƯỚC 8:** PaymentService → PaymentController: **Map** / response nội bộ.

**BƯỚC 9:** PaymentController → PaymentView: **200** + dữ liệu (checkoutUrl nếu bank).

**BƯỚC 10:** PaymentView → User: **redirect** sang PayOS (bank) hoặc hiển thị tóm tắt (cash).

### ▌ ĐI TỪNG BƯỚC — Cập nhật payment (11–15)

**BƯỚC 11:** User → PaymentView: yêu cầu đổi trạng thái / phương thức (theo màn admin hoặc luồng sửa đơn).

**BƯỚC 12:** PaymentView → PaymentController: `PUT /payments/update/{paymentId}`.

**BƯỚC 13:** PaymentController → PaymentService: `updatePayment(paymentId, …)`.

**BƯỚC 14:** PaymentService → PaymentRepository: `findByPaymentId` → **save** bản ghi đã chỉnh.

**BƯỚC 14.1–14.3:** PaymentRepository ↔ MySQL: query + persist.

**BƯỚC 15:** PaymentController → PaymentView: **200** + Payment đã cập nhật.

### ▌ CÂU CHỐT

✦ *"Luồng **1→10** là **tạo**; **11→15** là **sửa** — hai đoạn độc lập, dễ **demo** và **đối chiếu** với Postman."*

---

## 📊 4. STATE DIAGRAM — Trạng thái

### ▌ CÂU MỞ ĐẦU

*"State Diagram cho thấy **vòng đời** một **bản ghi Payment**: từ lúc user **bắt đầu** thanh toán, đã **chọn phương thức**, đang **chờ**, đã **thanh toán xong**, hoặc **hủy**."*

### ▌ CHỈ VÀO SƠ ĐỒ — Các trạng thái

*"Các nhãn tiêu biểu: **Initiated**, **MethodSelected**, **Pending**, **Paid**, **Cancelled**; có thể có **Refunded** nếu nhóm ghi chú “chưa implement”."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1: Initiated** — User bắt đầu luồng booking/payment (chưa chọn bank hay cash).

**BƯỚC 2:** User chọn **cash** hoặc **bank** → **MethodSelected** — phương thức đã xác định cho lần thanh toán này.

**BƯỚC 3:** Hệ thống tạo bản ghi **Payment** với `status = PENDING` → **Pending** — tiền chưa được coi là hoàn tất.

**BƯỚC 4 (nhánh bank):** PayOS xác nhận thành công (webhook / return URL) → cập nhật DB → **Paid**.

**BƯỚC 5 (nhánh cash):** Chủ xe / admin xác nhận đã thu tiền mặt → cập nhật DB → **Paid** (theo nghiệp vụ thực tế).

**BƯỚC 6:** User hoặc admin **hủy** giao dịch (nếu có trên sơ đồ) → **Cancelled**.

**BƯỚC 7:** **Refunded** — hoàn tiền — nhóm có thể ghi **chưa implement** như một trạng thái tương lai.

### ▌ CÂU CHỐT

✦ *"**payment method** lưu **trên từng Payment** — không có **một bảng** “thẻ mặc định của user” trong thiết kế hiện tại; đúng với **đặt cọc theo đơn**."*

---

## 📊 5. CLASS DIAGRAM — Cấu trúc lớp

### ▌ CÂU MỞ ĐẦU

*"Class Diagram thể hiện **tầng API** (**PaymentController**), **tầng nghiệp vụ** (**PaymentService**), **tầng truy cập dữ liệu** (**PaymentRepository**), **entity** và **DTO** đầu vào."*

### ▌ CHỈ VÀO SƠ ĐỒ — Các lớp và quan hệ

*"**PaymentController** phụ thuộc **PaymentService**. **PaymentService** phụ thuộc **PaymentRepository** và tích hợp **PayOS** (có thể vẽ dependency riêng). **PaymentRepository** trỏ tới **Payment** và **Database**."*

### ▌ ĐI TỪNG BƯỚC

**BƯỚC 1:** **PaymentController** — `createPayment`, `createCashPayment`, `updatePayment`, `getPaymentByOrderCode` (theo diagram nhóm).

**BƯỚC 2:** **PaymentService** — `createPaymentRequest`, `createCashPayment`, `confirmPaymentFromFrontend`, `updatePayment` — chứa logic gọi PayOS và quy tắc lưu.

**BƯỚC 3:** **PaymentRepository** — `save`, `findByOrderCode`, `findByPaymentId` — ánh xạ bảng payment.

**BƯỚC 4:** **PaymentRequest** — `orderCode`, `amount`, `returnUrl`, `cancelUrl`, `userId`, `carId`, …

**BƯỚC 5:** **CashPaymentRequest** — dữ liệu riêng cho thanh toán tiền mặt (ngày thuê, … tùy DTO).

**BƯỚC 6:** **Payment** — `paymentId`, `orderCode`, `amount`, `status`, `paymentMethod`, `paymentDate`, `userId`, `carId`.

**BƯỚC 7:** **PaymentMethod** (enum) — `cash`, `bank`.

**BƯỚC 8:** **Database** — lưu bảng **payments**; **không** có lớp **UserPaymentMethod** lưu thẻ ngân hàng cố định — nhóm **ghi chú** trên diagram nếu thầy cô hỏi.

### ▌ CÂU CHỐT

✦ *"Mỗi **Payment** là một **giao dịch**; **enum PaymentMethod** chuẩn hóa giá trị **cash/bank** — tránh lưu chuỗi tự do gây lỗi báo cáo."*

---

---
# GỢI Ý — Nếu nhóm tách **Register** và **Verify** ở hai slide

*(Nội dung đã trùng ở Use Case 01 và 07 — có thể **gộp** khi thuyết trình: “**UC1 + UC7** là một **story** đăng ký và xác thực.”)*

---

# GỢI Ý CÂU MỞ ĐẦU BUỔI THUYẾT TRÌNH (Tổng)

*"Thưa cô, đây là hệ thống **Drivon** — nền tảng **cho thuê xe**. Nhóm em mô hình hóa **tám luồng** nghiệp vụ: từ **đăng ký / đăng nhập / hồ sơ / mật khẩu**, đến **xác thực email**, **xem profile tổng hợp**, và **thanh toán PayOS & tiền mặt**. Mỗi use case em trình bày **đủ năm loại diagram**: **Activity** (luồng xử lý), **Sequence** (tương tác theo thời gian), **Communication** (message đánh số), **State** (trạng thái chuyển), **Class** (cấu trúc lớp và quan hệ)."*

---

# GỢI Ý CÂU KẾT BUỔI THUYẾT TRÌNH

*"Tóm lại, các diagram **không để trang trí** — mà **chứng minh** nhóm em đã **thiết kế theo tầng** (Controller → Service → Repository → Database), **bảo mật** (JWT, hash mật khẩu, token có hạn), và **tích hợp** thực tế (**PayOS**, **MySQL**). Em xin cảm ơn thầy cô."*

---

## Ký hiệu dùng trong file

| Ký hiệu | Ý nghĩa |
|--------|---------|
| ✦ | Lý do thiết kế / điểm nhấn |
| `code` | Endpoint, API, tên field |

---

*Bạn có thể copy từng mục vào PowerPoint / Word; chỉnh số slide và tên giảng viên cho phù hợp.*
