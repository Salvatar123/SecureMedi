/**
 * Input sanitization and validation utilities
 * Prevents XSS and injection attacks
 */

/**
 * Sanitize user input to prevent XSS
 * Removes potentially dangerous HTML characters and tags
 */
export function sanitizeInput(input: string): string {
  if (!input) return '';
  
  // Create a temporary div to leverage browser's HTML parsing
  const div = document.createElement('div');
  div.textContent = input;
  return div.innerHTML;
}

/**
 * Escape HTML special characters
 */
export function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  };
  return text.replace(/[&<>"']/g, char => map[char]);
}

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email) && email.length <= 254;
}

/**
 * Validate Ethereum address format (0x...)
 */
export function isValidEthereumAddress(address: string): boolean {
  return /^0x[a-fA-F0-9]{40}$/.test(address);
}

/**
 * Validate wallet address (supports Ethereum-like addresses)
 */
export function isValidAddress(address: string): boolean {
  return isValidEthereumAddress(address);
}

/**
 * Validate patient identifier format.
 * Accepts UUIDs and human-readable IDs like P001.
 */
export function isValidPatientIdentifier(patientId: string): boolean {
  const trimmed = patientId.trim();
  if (!trimmed || trimmed.length > 64) {
    return false;
  }

  const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  const readableIdPattern = /^[A-Za-z][A-Za-z0-9_-]{1,31}$/;

  return uuidPattern.test(trimmed) || readableIdPattern.test(trimmed);
}

/**
 * Validate JWT token format (basic)
 */
export function isValidJWT(token: string): boolean {
  const parts = token.split('.');
  return parts.length === 3 && parts.every(part => part.length > 0);
}

/**
 * Remove dangerous attributes from HTML strings
 * Used when rendering user-generated content that must include HTML
 */
export function sanitizeHtml(html: string): string {
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = html;
  
  // Remove script tags
  const scripts = tempDiv.querySelectorAll('script');
  scripts.forEach(script => script.remove());
  
  // Remove event handlers
  const allElements = tempDiv.querySelectorAll('*');
  allElements.forEach(element => {
    // Remove all attributes starting with 'on' (onclick, onerror, etc.)
    Array.from(element.attributes).forEach(attr => {
      if (attr.name.toLowerCase().startsWith('on')) {
        element.removeAttribute(attr.name);
      }
      // Block javascript: URIs
      if (attr.value.toLowerCase().includes('javascript:')) {
        element.removeAttribute(attr.name);
      }
    });
  });
  
  return tempDiv.innerHTML;
}

/**
 * Validate password strength
 * Requires: >=8 chars, uppercase, lowercase, number, special char
 */
export function isStrongPassword(password: string): boolean {
  const requirements = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /\d/.test(password),
    special: /[!@#$%^&*(),.?":{}|<>]/.test(password),
  };
  
  return Object.values(requirements).every(req => req);
}

/**
 * Get password strength feedback
 */
export function getPasswordStrengthFeedback(password: string): string[] {
  const feedback: string[] = [];
  
  if (password.length < 8) feedback.push('At least 8 characters required');
  if (!/[A-Z]/.test(password)) feedback.push('Add an uppercase letter');
  if (!/[a-z]/.test(password)) feedback.push('Add a lowercase letter');
  if (!/\d/.test(password)) feedback.push('Add a number');
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) feedback.push('Add a special character');
  
  return feedback;
}

/**
 * Validate URL (basic - prevent redirect attacks)
 */
export function isValidUrl(urlString: string): boolean {
  try {
    const url = new URL(urlString);
    // Only allow http and https protocols
    return ['http:', 'https:'].includes(url.protocol);
  } catch {
    return false;
  }
}

/**
 * Validate and normalize redirect URL (prevent open redirect)
 * Ensures redirect is to same origin
 */
export function getSafeRedirectUrl(url: string): string {
  try {
    const parsedUrl = new URL(url);
    // Only allow same-origin redirects
    if (parsedUrl.origin === window.location.origin) {
      return url;
    }
  } catch {
    // Invalid URL, use default
  }
  
  // Default to home page for security
  return '/';
}

/**
 * Limit string length (prevent DoS)
 */
export function limitStringLength(
  input: string,
  maxLength: number
): string {
  return input.substring(0, maxLength);
}
