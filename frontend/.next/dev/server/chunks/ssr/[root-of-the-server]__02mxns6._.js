module.exports = [
"[project]/SecureMedi/frontend/lib/auth.ts [ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

return __turbopack_context__.a(async (__turbopack_handle_async_dependencies__, __turbopack_async_result__) => { try {

__turbopack_context__.s([
    "useAuthStore",
    ()=>useAuthStore
]);
// Auth Store using Zustand
var __TURBOPACK__imported__module__$5b$externals$5d2f$zustand__$5b$external$5d$__$28$zustand$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$zustand$29$__ = __turbopack_context__.i("[externals]/zustand [external] (zustand, esm_import, [project]/SecureMedi/frontend/node_modules/zustand)");
var __TURBOPACK__imported__module__$5b$externals$5d2f$js$2d$cookie__$5b$external$5d$__$28$js$2d$cookie$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$js$2d$cookie$29$__ = __turbopack_context__.i("[externals]/js-cookie [external] (js-cookie, esm_import, [project]/SecureMedi/frontend/node_modules/js-cookie)");
var __turbopack_async_dependencies__ = __turbopack_handle_async_dependencies__([
    __TURBOPACK__imported__module__$5b$externals$5d2f$zustand__$5b$external$5d$__$28$zustand$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$zustand$29$__,
    __TURBOPACK__imported__module__$5b$externals$5d2f$js$2d$cookie__$5b$external$5d$__$28$js$2d$cookie$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$js$2d$cookie$29$__
]);
[__TURBOPACK__imported__module__$5b$externals$5d2f$zustand__$5b$external$5d$__$28$zustand$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$zustand$29$__, __TURBOPACK__imported__module__$5b$externals$5d2f$js$2d$cookie__$5b$external$5d$__$28$js$2d$cookie$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$js$2d$cookie$29$__] = __turbopack_async_dependencies__.then ? (await __turbopack_async_dependencies__)() : __turbopack_async_dependencies__;
;
;
const useAuthStore = (0, __TURBOPACK__imported__module__$5b$externals$5d2f$zustand__$5b$external$5d$__$28$zustand$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$zustand$29$__["create"])((set)=>({
        token: null,
        userAddress: null,
        role: null,
        isAuthenticated: false,
        login: (token, address, role)=>{
            __TURBOPACK__imported__module__$5b$externals$5d2f$js$2d$cookie__$5b$external$5d$__$28$js$2d$cookie$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$js$2d$cookie$29$__["default"].set("auth_token", token, {
                expires: 7
            });
            __TURBOPACK__imported__module__$5b$externals$5d2f$js$2d$cookie__$5b$external$5d$__$28$js$2d$cookie$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$js$2d$cookie$29$__["default"].set("user_address", address, {
                expires: 7
            });
            __TURBOPACK__imported__module__$5b$externals$5d2f$js$2d$cookie__$5b$external$5d$__$28$js$2d$cookie$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$js$2d$cookie$29$__["default"].set("user_role", role, {
                expires: 7
            });
            set({
                token,
                userAddress: address,
                role,
                isAuthenticated: true
            });
        },
        logout: ()=>{
            __TURBOPACK__imported__module__$5b$externals$5d2f$js$2d$cookie__$5b$external$5d$__$28$js$2d$cookie$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$js$2d$cookie$29$__["default"].remove("auth_token");
            __TURBOPACK__imported__module__$5b$externals$5d2f$js$2d$cookie__$5b$external$5d$__$28$js$2d$cookie$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$js$2d$cookie$29$__["default"].remove("user_address");
            __TURBOPACK__imported__module__$5b$externals$5d2f$js$2d$cookie__$5b$external$5d$__$28$js$2d$cookie$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$js$2d$cookie$29$__["default"].remove("user_role");
            set({
                token: null,
                userAddress: null,
                role: null,
                isAuthenticated: false
            });
        },
        initialize: ()=>{
            const token = __TURBOPACK__imported__module__$5b$externals$5d2f$js$2d$cookie__$5b$external$5d$__$28$js$2d$cookie$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$js$2d$cookie$29$__["default"].get("auth_token");
            const userAddress = __TURBOPACK__imported__module__$5b$externals$5d2f$js$2d$cookie__$5b$external$5d$__$28$js$2d$cookie$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$js$2d$cookie$29$__["default"].get("user_address");
            const role = __TURBOPACK__imported__module__$5b$externals$5d2f$js$2d$cookie__$5b$external$5d$__$28$js$2d$cookie$2c$__esm_import$2c$__$5b$project$5d2f$SecureMedi$2f$frontend$2f$node_modules$2f$js$2d$cookie$29$__["default"].get("user_role");
            if (token && userAddress && role) {
                set({
                    token,
                    userAddress,
                    role,
                    isAuthenticated: true
                });
            }
        }
    }));
__turbopack_async_result__();
} catch(e) { __turbopack_async_result__(e); } }, false);}),
"[project]/SecureMedi/frontend/pages/_app.tsx [ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

return __turbopack_context__.a(async (__turbopack_handle_async_dependencies__, __turbopack_async_result__) => { try {

__turbopack_context__.s([
    "default",
    ()=>__TURBOPACK__default__export__
]);
var __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__ = __turbopack_context__.i("[externals]/react/jsx-dev-runtime [external] (react/jsx-dev-runtime, cjs)");
// Next.js App Wrapper
var __TURBOPACK__imported__module__$5b$externals$5d2f$react__$5b$external$5d$__$28$react$2c$__cjs$29$__ = __turbopack_context__.i("[externals]/react [external] (react, cjs)");
var __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$lib$2f$auth$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/SecureMedi/frontend/lib/auth.ts [ssr] (ecmascript)");
var __turbopack_async_dependencies__ = __turbopack_handle_async_dependencies__([
    __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$lib$2f$auth$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__
]);
[__TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$lib$2f$auth$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__] = __turbopack_async_dependencies__.then ? (await __turbopack_async_dependencies__)() : __turbopack_async_dependencies__;
;
;
;
;
function MyApp({ Component, pageProps }) {
    const initialize = (0, __TURBOPACK__imported__module__$5b$project$5d2f$SecureMedi$2f$frontend$2f$lib$2f$auth$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["useAuthStore"])((state)=>state.initialize);
    (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react__$5b$external$5d$__$28$react$2c$__cjs$29$__["useEffect"])(()=>{
        initialize();
    }, [
        initialize
    ]);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])(Component, {
        ...pageProps
    }, void 0, false, {
        fileName: "[project]/SecureMedi/frontend/pages/_app.tsx",
        lineNumber: 15,
        columnNumber: 10
    }, this);
}
const __TURBOPACK__default__export__ = MyApp;
__turbopack_async_result__();
} catch(e) { __turbopack_async_result__(e); } }, false);}),
"[externals]/zustand [external] (zustand, esm_import, [project]/SecureMedi/frontend/node_modules/zustand)", ((__turbopack_context__) => {
"use strict";

return __turbopack_context__.a(async (__turbopack_handle_async_dependencies__, __turbopack_async_result__) => { try {

const mod = await __turbopack_context__.y("zustand-88bea747f9c022ed");

__turbopack_context__.n(mod);
__turbopack_async_result__();
} catch(e) { __turbopack_async_result__(e); } }, true);}),
"[externals]/js-cookie [external] (js-cookie, esm_import, [project]/SecureMedi/frontend/node_modules/js-cookie)", ((__turbopack_context__) => {
"use strict";

return __turbopack_context__.a(async (__turbopack_handle_async_dependencies__, __turbopack_async_result__) => { try {

const mod = await __turbopack_context__.y("js-cookie-8cbae5434bb16b7e");

__turbopack_context__.n(mod);
__turbopack_async_result__();
} catch(e) { __turbopack_async_result__(e); } }, true);}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__02mxns6._.js.map