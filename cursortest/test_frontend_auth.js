// 测试前端认证状态的脚本
// 在浏览器控制台中运行

// 检查localStorage中的认证信息
console.log('Auth Token:', localStorage.getItem('auth_token'));
console.log('User Info:', localStorage.getItem('user'));

// 检查AuthService实例
const authService = AuthService.getInstance();
console.log('AuthService Token:', authService.token);
console.log('AuthService User:', authService.user);
console.log('Auth Headers:', authService.getAuthHeaders());

// 测试API调用
fetch('http://localhost:3000/api/auth/me', {
  headers: authService.getAuthHeaders()
})
.then(response => response.json())
.then(data => console.log('Current User API Response:', data))
.catch(error => console.error('API Error:', error));
