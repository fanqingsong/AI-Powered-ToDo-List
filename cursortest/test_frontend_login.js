// 模拟前端登录过程
const API_BASE = 'http://localhost:3000/api';

async function simulateFrontendLogin() {
    console.log('开始模拟前端登录...');
    
    try {
        // 1. 登录
        console.log('1. 正在登录...');
        const loginResponse = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                username: 'qingsong',
                password: 'qingsong'
            })
        });
        
        if (!loginResponse.ok) {
            throw new Error(`登录失败: ${loginResponse.status}`);
        }
        
        const loginData = await loginResponse.json();
        console.log('登录成功:', loginData);
        
        // 2. 保存token到localStorage (模拟)
        const token = loginData.access_token;
        console.log('Token:', token.substring(0, 20) + '...');
        
        // 3. 获取用户信息
        console.log('2. 正在获取用户信息...');
        const userResponse = await fetch(`${API_BASE}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            }
        });
        
        if (!userResponse.ok) {
            throw new Error(`获取用户信息失败: ${userResponse.status}`);
        }
        
        const userData = await userResponse.json();
        console.log('用户信息:', userData);
        
        // 4. 测试笔记API
        console.log('3. 正在测试笔记API...');
        const notesResponse = await fetch(`${API_BASE}/notes/stats/overview`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!notesResponse.ok) {
            throw new Error(`笔记API失败: ${notesResponse.status}`);
        }
        
        const notesData = await notesResponse.json();
        console.log('笔记统计:', notesData);
        
        console.log('✅ 所有测试通过！');
        
    } catch (error) {
        console.error('❌ 测试失败:', error.message);
    }
}

// 运行测试
simulateFrontendLogin();
