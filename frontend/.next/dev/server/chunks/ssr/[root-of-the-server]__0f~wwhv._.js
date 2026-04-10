module.exports = [
"[externals]/fs [external] (fs, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("fs", () => require("fs"));

module.exports = mod;
}),
"[externals]/stream [external] (stream, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("stream", () => require("stream"));

module.exports = mod;
}),
"[externals]/zlib [external] (zlib, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("zlib", () => require("zlib"));

module.exports = mod;
}),
"[externals]/react-dom [external] (react-dom, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("react-dom", () => require("react-dom"));

module.exports = mod;
}),
"[project]/SecureMedi/frontend/components/Header.tsx [ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

return __turbopack_context__.a(async (__turbopack_handle_async_dependencies__, __turbopack_async_result__) => { try {

// Header Component
__turbopack_context__.s([
    "Header",
    ()=>Header
]);
var __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__ = __turbopack_context__.i("[externals]/react/jsx-dev-runtime [external] (react/jsx-dev-runtime, cjs)");
var __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$next$2f$link$2e$js__$5b$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/SecureMedi/frontend/node_modules/next/link.js [ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$lib$2f$auth$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/SecureMedi/frontend/lib/auth.ts [ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$next$2f$router$2e$js__$5b$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/SecureMedi/frontend/node_modules/next/router.js [ssr] (ecmascript)");
var __turbopack_async_dependencies__ = __turbopack_handle_async_dependencies__([
    __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$lib$2f$auth$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__
]);
[__TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$lib$2f$auth$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__] = __turbopack_async_dependencies__.then ? (await __turbopack_async_dependencies__)() : __turbopack_async_dependencies__;
;
;
;
;
const Header = ()=>{
    const { isAuthenticated, role, logout } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$lib$2f$auth$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["useAuthStore"])();
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$next$2f$router$2e$js__$5b$ssr$5d$__$28$ecmascript$29$__["useRouter"])();
    const handleLogout = ()=>{
        logout();
        router.push("/login");
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("header", {
        className: "border-b border-border bg-card sticky top-0 z-40",
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
            className: "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8",
            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                className: "flex justify-between items-center h-16",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$next$2f$link$2e$js__$5b$ssr$5d$__$28$ecmascript$29$__["default"], {
                        href: "/",
                        className: "flex items-center space-x-2",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                                className: "w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center",
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("span", {
                                    className: "text-white font-bold text-sm",
                                    children: "SM"
                                }, void 0, false, {
                                    fileName: "[project]/SecureMedi/frontend/components/Header.tsx",
                                    lineNumber: 23,
                                    columnNumber: 15
                                }, ("TURBOPACK compile-time value", void 0))
                            }, void 0, false, {
                                fileName: "[project]/SecureMedi/frontend/components/Header.tsx",
                                lineNumber: 22,
                                columnNumber: 13
                            }, ("TURBOPACK compile-time value", void 0)),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("span", {
                                className: "text-xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent",
                                children: "SecureMedi"
                            }, void 0, false, {
                                fileName: "[project]/SecureMedi/frontend/components/Header.tsx",
                                lineNumber: 25,
                                columnNumber: 13
                            }, ("TURBOPACK compile-time value", void 0))
                        ]
                    }, void 0, true, {
                        fileName: "[project]/SecureMedi/frontend/components/Header.tsx",
                        lineNumber: 21,
                        columnNumber: 11
                    }, ("TURBOPACK compile-time value", void 0)),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                        className: "flex items-center space-x-4",
                        children: isAuthenticated ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["Fragment"], {
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("span", {
                                    className: "text-sm text-foreground/70",
                                    children: [
                                        "Role: ",
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("span", {
                                            className: "font-semibold",
                                            children: role
                                        }, void 0, false, {
                                            fileName: "[project]/SecureMedi/frontend/components/Header.tsx",
                                            lineNumber: 34,
                                            columnNumber: 25
                                        }, ("TURBOPACK compile-time value", void 0))
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/SecureMedi/frontend/components/Header.tsx",
                                    lineNumber: 33,
                                    columnNumber: 17
                                }, ("TURBOPACK compile-time value", void 0)),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("button", {
                                    onClick: handleLogout,
                                    className: "px-4 py-2 bg-danger/20 text-danger rounded-lg hover:bg-danger/30 transition-colors text-sm font-medium",
                                    children: "Logout"
                                }, void 0, false, {
                                    fileName: "[project]/SecureMedi/frontend/components/Header.tsx",
                                    lineNumber: 36,
                                    columnNumber: 17
                                }, ("TURBOPACK compile-time value", void 0))
                            ]
                        }, void 0, true) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$next$2f$link$2e$js__$5b$ssr$5d$__$28$ecmascript$29$__["default"], {
                            href: "/login",
                            className: "px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors text-sm font-medium",
                            children: "Login"
                        }, void 0, false, {
                            fileName: "[project]/SecureMedi/frontend/components/Header.tsx",
                            lineNumber: 44,
                            columnNumber: 15
                        }, ("TURBOPACK compile-time value", void 0))
                    }, void 0, false, {
                        fileName: "[project]/SecureMedi/frontend/components/Header.tsx",
                        lineNumber: 30,
                        columnNumber: 11
                    }, ("TURBOPACK compile-time value", void 0))
                ]
            }, void 0, true, {
                fileName: "[project]/SecureMedi/frontend/components/Header.tsx",
                lineNumber: 20,
                columnNumber: 9
            }, ("TURBOPACK compile-time value", void 0))
        }, void 0, false, {
            fileName: "[project]/SecureMedi/frontend/components/Header.tsx",
            lineNumber: 19,
            columnNumber: 7
        }, ("TURBOPACK compile-time value", void 0))
    }, void 0, false, {
        fileName: "[project]/SecureMedi/frontend/components/Header.tsx",
        lineNumber: 18,
        columnNumber: 5
    }, ("TURBOPACK compile-time value", void 0));
};
__turbopack_async_result__();
} catch(e) { __turbopack_async_result__(e); } }, false);}),
"[project]/SecureMedi/frontend/lib/api.ts [ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

return __turbopack_context__.a(async (__turbopack_handle_async_dependencies__, __turbopack_async_result__) => { try {

__turbopack_context__.s([
    "apiClient",
    ()=>apiClient
]);
// API Client for Frontend
var __TURBOPACK__imported__module__$5b$externals$5d2f$axios__$5b$external$5d$__$28$axios$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$axios$29$__ = __turbopack_context__.i("[externals]/axios [external] (axios, esm_import, [project]/SecureMedi/frontend/node_modules/axios)");
var __TURBOPACK__imported__module__$5b$externals$5d2f$js$2d$cookie__$5b$external$5d$__$28$js$2d$cookie$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$js$2d$cookie$29$__ = __turbopack_context__.i("[externals]/js-cookie [external] (js-cookie, esm_import, [project]/SecureMedi/frontend/node_modules/js-cookie)");
var __turbopack_async_dependencies__ = __turbopack_handle_async_dependencies__([
    __TURBOPACK__imported__module__$5b$externals$5d2f$axios__$5b$external$5d$__$28$axios$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$axios$29$__,
    __TURBOPACK__imported__module__$5b$externals$5d2f$js$2d$cookie__$5b$external$5d$__$28$js$2d$cookie$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$js$2d$cookie$29$__
]);
[__TURBOPACK__imported__module__$5b$externals$5d2f$axios__$5b$external$5d$__$28$axios$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$axios$29$__, __TURBOPACK__imported__module__$5b$externals$5d2f$js$2d$cookie__$5b$external$5d$__$28$js$2d$cookie$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$js$2d$cookie$29$__] = __turbopack_async_dependencies__.then ? (await __turbopack_async_dependencies__)() : __turbopack_async_dependencies__;
;
;
const API_URL = ("TURBOPACK compile-time value", "http://localhost:8000") || "http://localhost:8000";
class ApiClient {
    client;
    constructor(){
        this.client = __TURBOPACK__imported__module__$5b$externals$5d2f$axios__$5b$external$5d$__$28$axios$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$axios$29$__["default"].create({
            baseURL: API_URL,
            headers: {
                "Content-Type": "application/json"
            }
        });
        // Add token to requests
        this.client.interceptors.request.use((config)=>{
            const token = __TURBOPACK__imported__module__$5b$externals$5d2f$js$2d$cookie__$5b$external$5d$__$28$js$2d$cookie$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$js$2d$cookie$29$__["default"].get("auth_token");
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        });
        // Handle errors globally
        this.client.interceptors.response.use((response)=>response, (error)=>{
            if (error.response?.status === 401) {
                // Clear auth
                __TURBOPACK__imported__module__$5b$externals$5d2f$js$2d$cookie__$5b$external$5d$__$28$js$2d$cookie$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$js$2d$cookie$29$__["default"].remove("auth_token");
                window.location.href = "/login";
            }
            return Promise.reject(error);
        });
    }
    // Auth endpoints
    async loginDoctor(address, key) {
        return this.client.post("/api/auth/login/doctor", {
            address,
            key
        });
    }
    async loginPatient(patientId, privateKey) {
        return this.client.post("/api/auth/login/patient", {
            address: patientId,
            key: privateKey
        });
    }
    async refreshToken(refreshToken) {
        try {
            const response = await this.client.post("/api/auth/refresh", {
                refresh_token: refreshToken
            });
            return response.data;
        } catch (error) {
            return {
                success: false,
                message: "Failed to refresh token"
            };
        }
    }
    async logout(token) {
        try {
            const response = await this.client.post("/api/auth/logout", null, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            return response.data;
        } catch (error) {
            return {
                success: false,
                message: "Logout failed"
            };
        }
    }
    async verifyToken(token) {
        try {
            const response = await this.client.post("/api/auth/verify", null, {
                params: {
                    token
                }
            });
            return response.data;
        } catch (error) {
            return {
                valid: false
            };
        }
    }
    // Health endpoints
    async getLatestVitals() {
        return this.client.get("/api/health/vitals/latest");
    }
    async getVitalsHistory(limit = 100) {
        return this.client.get("/api/health/vitals/history", {
            params: {
                limit
            }
        });
    }
    async getHealthStats() {
        return this.client.get("/api/health/statistics");
    }
    async getAlerts(patientId) {
        return this.client.get("/api/health/alerts", {
            params: {
                patient_id: patientId
            }
        });
    }
    // Patient endpoints
    async getPatientRecord(patientId) {
        return this.client.get(`/api/patients/${patientId}`);
    }
    async getPatientVitals(patientId, limit = 100) {
        return this.client.get(`/api/patients/${patientId}/vitals`, {
            params: {
                limit
            }
        });
    }
    async exportPatientData(patientId) {
        return this.client.post(`/api/patients/${patientId}/export`);
    }
    // Doctor endpoints
    async getDoctorInfo(address) {
        return this.client.get(`/api/doctors/${address}`);
    }
    async getAccessLogs(doctorAddress, limit = 100) {
        return this.client.get(`/api/doctors/${doctorAddress}/access-logs`, {
            params: {
                limit
            }
        });
    }
    async logPatientAccess(doctorAddress, patientId, accessType = "NORMAL", reason = "") {
        return this.client.post(`/api/doctors/${doctorAddress}/access-patient/${patientId}`, {
            access_type: accessType,
            reason
        });
    }
    async emergencyAccess(patientId, key) {
        return this.client.post("/api/doctors/emergency-access", {
            patient_id: patientId,
            key
        });
    }
    async requestAccessKey() {
        try {
            const response = await this.client.post("/api/auth/request-key");
            return response.data;
        } catch (error) {
            return {
                success: false,
                message: "An error occurred while requesting an access key."
            };
        }
    }
}
const apiClient = new ApiClient();
__turbopack_async_result__();
} catch(e) { __turbopack_async_result__(e); } }, false);}),
"[project]/SecureMedi/frontend/pages/login.tsx [ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

return __turbopack_context__.a(async (__turbopack_handle_async_dependencies__, __turbopack_async_result__) => { try {

__turbopack_context__.s([
    "default",
    ()=>LoginPage
]);
var __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__ = __turbopack_context__.i("[externals]/react/jsx-dev-runtime [external] (react/jsx-dev-runtime, cjs)");
// Login Page
var __TURBOPACK__imported__module__$5b$externals$5d2f$react__$5b$external$5d$__$28$react$2c$__cjs$29$__ = __turbopack_context__.i("[externals]/react [external] (react, cjs)");
var __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$next$2f$router$2e$js__$5b$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/SecureMedi/frontend/node_modules/next/router.js [ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$next$2f$head$2e$js__$5b$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/SecureMedi/frontend/node_modules/next/head.js [ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$components$2f$Header$2e$tsx__$5b$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/SecureMedi/frontend/components/Header.tsx [ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$lib$2f$auth$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/SecureMedi/frontend/lib/auth.ts [ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$lib$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/SecureMedi/frontend/lib/api.ts [ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$externals$5d2f$react$2d$hot$2d$toast__$5b$external$5d$__$28$react$2d$hot$2d$toast$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$react$2d$hot$2d$toast$29$__ = __turbopack_context__.i("[externals]/react-hot-toast [external] (react-hot-toast, esm_import, [project]/SecureMedi/frontend/node_modules/react-hot-toast)");
var __turbopack_async_dependencies__ = __turbopack_handle_async_dependencies__([
    __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$components$2f$Header$2e$tsx__$5b$ssr$5d$__$28$ecmascript$29$__,
    __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$lib$2f$auth$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__,
    __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$lib$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__,
    __TURBOPACK__imported__module__$5b$externals$5d2f$react$2d$hot$2d$toast__$5b$external$5d$__$28$react$2d$hot$2d$toast$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$react$2d$hot$2d$toast$29$__
]);
[__TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$components$2f$Header$2e$tsx__$5b$ssr$5d$__$28$ecmascript$29$__, __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$lib$2f$auth$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__, __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$lib$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2d$hot$2d$toast__$5b$external$5d$__$28$react$2d$hot$2d$toast$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$react$2d$hot$2d$toast$29$__] = __turbopack_async_dependencies__.then ? (await __turbopack_async_dependencies__)() : __turbopack_async_dependencies__;
;
;
;
;
;
;
;
;
function LoginPage() {
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$next$2f$router$2e$js__$5b$ssr$5d$__$28$ecmascript$29$__["useRouter"])();
    const login = (0, __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$lib$2f$auth$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["useAuthStore"])((state)=>state.login);
    const [isDoctor, setIsDoctor] = (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react__$5b$external$5d$__$28$react$2c$__cjs$29$__["useState"])(true);
    const [address, setAddress] = (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react__$5b$external$5d$__$28$react$2c$__cjs$29$__["useState"])("");
    const [key, setKey] = (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react__$5b$external$5d$__$28$react$2c$__cjs$29$__["useState"])("");
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react__$5b$external$5d$__$28$react$2c$__cjs$29$__["useState"])(false);
    const handleLogin = async (e)=>{
        e.preventDefault();
        if (!address || !key) {
            __TURBOPACK__imported__module__$5b$externals$5d2f$react$2d$hot$2d$toast__$5b$external$5d$__$28$react$2d$hot$2d$toast$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$react$2d$hot$2d$toast$29$__["default"].error("Please fill all fields");
            return;
        }
        setLoading(true);
        try {
            const response = isDoctor ? await __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$lib$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["apiClient"].loginDoctor(address, key) : await __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$lib$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["apiClient"].loginPatient(address, key);
            const data = response.data;
            if (data.success) {
                login(data.token, data.user_address, data.role);
                __TURBOPACK__imported__module__$5b$externals$5d2f$react$2d$hot$2d$toast__$5b$external$5d$__$28$react$2d$hot$2d$toast$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$react$2d$hot$2d$toast$29$__["default"].success(`Welcome, ${data.role}!`);
                router.push("/dashboard");
            } else {
                __TURBOPACK__imported__module__$5b$externals$5d2f$react$2d$hot$2d$toast__$5b$external$5d$__$28$react$2d$hot$2d$toast$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$react$2d$hot$2d$toast$29$__["default"].error(data.message || "Login failed");
            }
        } catch (error) {
            __TURBOPACK__imported__module__$5b$externals$5d2f$react$2d$hot$2d$toast__$5b$external$5d$__$28$react$2d$hot$2d$toast$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$react$2d$hot$2d$toast$29$__["default"].error("Login failed. Please check your credentials.");
            console.error(error);
        } finally{
            setLoading(false);
        }
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["Fragment"], {
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$next$2f$head$2e$js__$5b$ssr$5d$__$28$ecmascript$29$__["default"], {
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("title", {
                    children: "Login - SecureMedi"
                }, void 0, false, {
                    fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                    lineNumber: 54,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                lineNumber: 53,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$components$2f$Header$2e$tsx__$5b$ssr$5d$__$28$ecmascript$29$__["Header"], {}, void 0, false, {
                fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                lineNumber: 57,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                className: "min-h-screen bg-background flex items-center justify-center p-4",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                    className: "max-w-md w-full space-y-8",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                            className: "text-center",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                                    className: "inline-block p-3 bg-gradient-to-br from-primary to-secondary rounded-lg mb-4",
                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("span", {
                                        className: "text-white font-bold text-2xl",
                                        children: "SM"
                                    }, void 0, false, {
                                        fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                                        lineNumber: 64,
                                        columnNumber: 15
                                    }, this)
                                }, void 0, false, {
                                    fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                                    lineNumber: 63,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("h1", {
                                    className: "text-3xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent",
                                    children: "SecureMedi"
                                }, void 0, false, {
                                    fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                                    lineNumber: 66,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("p", {
                                    className: "text-foreground/70 mt-2",
                                    children: "Secure Medical Data Platform"
                                }, void 0, false, {
                                    fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                                    lineNumber: 69,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                            lineNumber: 62,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("form", {
                            onSubmit: handleLogin,
                            className: "space-y-6 p-6 border border-border rounded-lg bg-card/50",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                                    className: "flex gap-2 bg-border/50 p-1 rounded-lg",
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("button", {
                                            type: "button",
                                            onClick: ()=>setIsDoctor(true),
                                            className: `flex-1 py-2 rounded font-medium transition-colors ${isDoctor ? "bg-primary text-white" : "text-foreground/70 hover:text-foreground"}`,
                                            children: "Doctor"
                                        }, void 0, false, {
                                            fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                                            lineNumber: 76,
                                            columnNumber: 15
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("button", {
                                            type: "button",
                                            onClick: ()=>setIsDoctor(false),
                                            className: `flex-1 py-2 rounded font-medium transition-colors ${!isDoctor ? "bg-primary text-white" : "text-foreground/70 hover:text-foreground"}`,
                                            children: "Patient"
                                        }, void 0, false, {
                                            fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                                            lineNumber: 87,
                                            columnNumber: 15
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                                    lineNumber: 75,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("label", {
                                            className: "block text-sm font-medium text-foreground mb-2",
                                            children: isDoctor ? "Wallet Address" : "Patient ID"
                                        }, void 0, false, {
                                            fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                                            lineNumber: 102,
                                            columnNumber: 15
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("input", {
                                            type: "text",
                                            value: address,
                                            onChange: (e)=>setAddress(e.target.value),
                                            placeholder: isDoctor ? "0x..." : "P001",
                                            className: "w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:border-primary text-foreground"
                                        }, void 0, false, {
                                            fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                                            lineNumber: 105,
                                            columnNumber: 15
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                                    lineNumber: 101,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("label", {
                                            className: "block text-sm font-medium text-foreground mb-2",
                                            children: isDoctor ? "Access Key" : "Private Key"
                                        }, void 0, false, {
                                            fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                                            lineNumber: 116,
                                            columnNumber: 15
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("input", {
                                            type: "password",
                                            value: key,
                                            onChange: (e)=>setKey(e.target.value),
                                            placeholder: "Enter your key",
                                            className: "w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:border-primary text-foreground"
                                        }, void 0, false, {
                                            fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                                            lineNumber: 119,
                                            columnNumber: 15
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                                    lineNumber: 115,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("button", {
                                    type: "submit",
                                    disabled: loading,
                                    className: "w-full py-2 bg-gradient-to-r from-primary to-secondary text-white rounded-lg font-semibold hover:opacity-90 disabled:opacity-50 transition-all",
                                    children: loading ? "Logging in..." : "Login"
                                }, void 0, false, {
                                    fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                                    lineNumber: 129,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                            lineNumber: 73,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                            className: "p-4 bg-border/20 rounded-lg border border-border/50",
                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("p", {
                                className: "text-xs text-foreground/60 text-center",
                                children: "This is a secure healthcare platform. Use your registered credentials to access your account."
                            }, void 0, false, {
                                fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                                lineNumber: 140,
                                columnNumber: 13
                            }, this)
                        }, void 0, false, {
                            fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                            lineNumber: 139,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                    lineNumber: 60,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/SecureMedi/frontend/pages/login.tsx",
                lineNumber: 59,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true);
}
__turbopack_async_result__();
} catch(e) { __turbopack_async_result__(e); } }, false);}),
"[externals]/next/dist/shared/lib/no-fallback-error.external.js [external] (next/dist/shared/lib/no-fallback-error.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/shared/lib/no-fallback-error.external.js", () => require("next/dist/shared/lib/no-fallback-error.external.js"));

module.exports = mod;
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__0f~wwhv._.js.map