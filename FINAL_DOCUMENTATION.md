# Technical Documentation for Auth Service

## Introduction

This document provides a comprehensive technical overview of the `auth-service` Spring Boot application. It consolidates various raw Markdown documentation snippets into a single, cohesive resource, detailing the application's architecture, components, and functionalities. The purpose of this documentation is to serve as a central reference for developers, aiding in understanding, maintenance, and future development of the authentication service.

## Table of Contents

1.  [Entities](#entities)
2.  [Repositories](#repositories)
3.  [Services](#services)
4.  [Controllers](#controllers)
5.  [Configuration](#configuration)
6.  [Security](#security)
7.  [DTOs](#dtos)
8.  [Exceptions](#exceptions)
9.  [Application Entrypoint](#application-entrypoint)
10. [Tests](#tests)

---

## Entities

No documentation snippets were provided for the Entities (Data Model) layer.

---

## Repositories

No documentation snippets were provided for the Repositories (Data Access Layer) layer.

---

## Services

### `UserServiceClient.java` Documentation

## Overview

The `UserServiceClient` class is a Spring `@Service` component responsible for communicating with a separate user authentication service. It acts as a client to validate user credentials by making HTTP requests to the user service's `/users/validate` endpoint. This class leverages Spring's `WebClient` for performing non-blocking, reactive HTTP calls.

## Dependencies

*   **`com.example.auth_service.dto.LoginRequest`**: A Data Transfer Object (DTO) representing the user's login credentials (e.g., username and password) sent to the user service for validation.
*   **`com.example.auth_service.dto.UserValidationResponse`**: A DTO representing the response received from the user service after a validation attempt, typically indicating success or failure and possibly user details.
*   **`org.springframework.stereotype.Service`**: An annotation that marks this class as a Spring service component, making it eligible for component scanning and dependency injection.
*   **`org.springframework.web.reactive.function.client.WebClient`**: A non-blocking, reactive HTTP client provided by Spring WebFlux. It is used to make HTTP requests to external services.

## Class Structure

```java
@Service
public class UserServiceClient {

    private final WebClient webClient;

    public UserServiceClient(WebClient.Builder builder) {
        // ...
    }

    public UserValidationResponse validateUser(LoginRequest loginRequest) {
        // ...
    }
}
```

## Constructor

### `UserServiceClient(WebClient.Builder builder)`

This constructor is responsible for initializing the `WebClient` instance used for making HTTP requests.

*   **Parameters**:
    *   `WebClient.Builder builder`: An injected `WebClient.Builder` instance provided by Spring. This builder is used to configure and build the `WebClient`.
*   **Initialization**:
    *   The `webClient` field is initialized by building a `WebClient` instance.
    *   `builder.baseUrl("http://user-service")`: Sets the base URL for all requests made by this `WebClient` instance to `http://user-service`. This assumes that `user-service` is the service name resolvable within a container orchestration environment like Docker or Kubernetes.

## Methods

### `validateUser(LoginRequest loginRequest)`

This method sends a user login request to the external user service for validation.

*   **Purpose**: To validate a user's login credentials against the user authentication service.
*   **Parameters**:
    *   `LoginRequest loginRequest`: An object containing the user's credentials (e.g., username, password) to be validated.
*   **Return Type**:
    *   `UserValidationResponse`: An object containing the response from the user service, indicating whether the user was successfully validated.
*   **Process**:
    1.  `webClient.post()`: Initiates a POST request.
    2.  `.uri("/users/validate")`: Appends `/users/validate` to the base URL, forming the complete endpoint URL (e.g., `http://user-service/users/validate`).
    3.  `.bodyValue(loginRequest)`: Sets the `LoginRequest` object as the request body. Spring will automatically serialize this DTO to JSON.
    4.  `.retrieve()`: Executes the request and retrieves the response.
    5.  `.bodyToMono(UserValidationResponse.class)`: Specifies that the response body should be converted into a `Mono` of `UserValidationResponse`. `Mono` is a reactive type representing a stream of 0 or 1 item.
    6.  `.block()`: Blocks the execution until the `Mono` emits its item (the `UserValidationResponse`) or completes with an error. While `WebClient` is typically used in a non-blocking reactive context, `block()` is used here to get the result synchronously.

## Usage Example

This service would typically be injected into another service or controller within the `auth-service` application to perform user validation.

```java
// Example of how UserServiceClient might be used in another service
@Service
public class AuthService {

    private final UserServiceClient userServiceClient;

    public AuthService(UserServiceClient userServiceClient) {
        this.userServiceClient = userServiceClient;
    }

    public boolean authenticate(LoginRequest loginRequest) {
        UserValidationResponse response = userServiceClient.validateUser(loginRequest);
        return response != null && response.isValid(); // Assuming UserValidationResponse has an isValid() method
    }
}
```

---

## Controllers

### AuthController

## Overview

The `AuthController` class is a Spring `RestController` responsible for handling authentication-related requests within the `auth_service` application. It is mapped to the `/auth` endpoint.

## Location

`src/main/java/com/example/auth_service/controller/AuthController.java`

## Current Status

As of the current version, the `AuthController` class is initialized but does not contain any defined endpoints or methods. It serves as a placeholder for future authentication functionalities such as user registration, login, token validation, and password management.

## Future Enhancements (Planned)

The following functionalities are expected to be implemented within this controller:

*   **User Registration:** Endpoint for new user sign-ups.
*   **User Login:** Endpoint for authenticating users and issuing tokens.
*   **Token Validation:** Endpoint for verifying the validity of authentication tokens.
*   **Password Reset:** Endpoints for initiating and completing password reset processes.
*   **User Details:** Endpoints for retrieving or updating authenticated user information.

## Usage

Once endpoints are implemented, this controller will be accessible via the base URL `/auth` followed by the specific endpoint paths (e.g., `/auth/register`, `/auth/login`).

---

## Configuration

No documentation snippets were provided for the Configuration layer.

---

## Security

### `JwtAuthorizationFilter.java`

This document provides a detailed overview of the `JwtAuthorizationFilter` class, which is a core component of the authentication and authorization mechanism within the `auth_service`.

## 1. Overview

The `JwtAuthorizationFilter` extends Spring's `OncePerRequestFilter` to intercept incoming HTTP requests and validate JSON Web Tokens (JWTs) present in the `Authorization` header. Its primary responsibility is to ensure that requests carrying a valid JWT are authenticated and that the user's identity is established in the Spring Security context. If a token is invalid or missing, it handles the unauthorized access appropriately.

## 2. Dependencies

*   **`jakarta.servlet.*`**: Standard Java Servlet API for handling HTTP requests and responses.
*   **`io.jsonwebtoken.Claims`**: Used for extracting claims (payload) from a JWT.
*   **`org.springframework.security.authentication.UsernamePasswordAuthenticationToken`**: Represents an authentication request or an authenticated user token.
*   **`org.springframework.security.core.context.SecurityContextHolder`**: Provides access to the security context, where the authenticated user's information is stored.
*   **`org.springframework.web.filter.OncePerRequestFilter`**: A base class for filters that are guaranteed to be executed only once per request.
*   **`com.example.auth_service.security.JwtUtil`**: A utility class responsible for JWT creation, validation, and parsing.

## 3. Class Definition

```java
public class JwtAuthorizationFilter extends OncePerRequestFilter {
    private final JwtUtil jwtUtil;

    public JwtAuthorizationFilter(JwtUtil jwtUtil) {
        this.jwtUtil = jwtUtil;
    }

    // ... doFilterInternal method ...
}
```

### 3.1. Constructor

*   **`public JwtAuthorizationFilter(JwtUtil jwtUtil)`**:
    *   **Parameters**:
        *   `jwtUtil`: An instance of `JwtUtil` used for all JWT-related operations (validation, parsing).
    *   **Description**: Initializes the filter with a `JwtUtil` instance, making it ready to process JWTs.

## 4. `doFilterInternal` Method

```java
@Override
protected void doFilterInternal(HttpServletRequest req,
                                HttpServletResponse res,
                                FilterChain chain)
        throws ServletException, IOException {
    String header = req.getHeader("Authorization");
    if (header != null && header.startsWith("Bearer ")) {
        String token = header.substring(7);
        try {
            Claims claims = jwtUtil.validateToken(token).getBody();
            var user = new UsernamePasswordAuthenticationToken(
                    claims.getSubject(), null, List.of());
            SecurityContextHolder.getContext().setAuthentication(user);
        } catch (Exception e) {
            res.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            return;
        }
    }
    chain.doFilter(req, res);
}
```

### 4.1. Method Signature

*   **`protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain chain)`**:
    *   **Parameters**:
        *   `req`: The `HttpServletRequest` being processed.
        *   `res`: The `HttpServletResponse` to which the response will be written.
        *   `chain`: The `FilterChain` to proceed with the next filter in the chain.
    *   **Throws**: `ServletException`, `IOException`

### 4.2. Logic and Flow

1.  **Extract Authorization Header**:
    *   It retrieves the `Authorization` header from the incoming `HttpServletRequest`.
    *   It checks if the header is present and starts with `"Bearer "`, indicating a JWT.

2.  **Extract JWT Token**:
    *   If a "Bearer" token is found, the actual JWT string is extracted by removing the "Bearer " prefix.

3.  **Validate Token and Set Authentication**:
    *   A `try-catch` block is used to handle potential `Exception`s during token validation.
    *   **Validation**: The `jwtUtil.validateToken(token)` method is called to validate the token's signature and expiration. If valid, it returns the token's `Claims`.
    *   **Authentication Object Creation**: A `UsernamePasswordAuthenticationToken` is created using the subject (username) from the JWT claims. In this implementation, authorities are not extracted from the token and are set as an empty list (`List.of()`).
    *   **Set Security Context**: The created `Authentication` object is then set into the `SecurityContextHolder`, effectively authenticating the user for the current request within Spring Security's context.

4.  **Handle Unauthorized Access**:
    *   If `jwtUtil.validateToken` throws an `Exception` (e.g., token expired, invalid signature), the `catch` block is executed.
    *   The `HttpServletResponse` status is set to `HttpServletResponse.SC_UNAUTHORIZED` (401), and the filter chain is terminated (`return`), preventing further processing of the request.

5.  **Continue Filter Chain**:
    *   If no `Authorization` header is found, or if the token is successfully validated, `chain.doFilter(req, res)` is called to pass the request to the next filter in the chain or to the target servlet/controller.

## 5. Usage and Integration

This filter is typically registered in the Spring Security configuration to be executed before other authorization checks. It acts as an entry point for JWT-based authentication, ensuring that subsequent security layers can rely on the `SecurityContextHolder` to contain the authenticated user's details.

### `SecurityConfig.java`

This document provides a detailed overview of the `SecurityConfig` class, which is responsible for configuring the security settings for the authentication service. It leverages Spring Security to define authentication mechanisms, authorization rules, and integrates JWT (JSON Web Token) for stateless API security.

## Class Overview

The `SecurityConfig` class is a central component for defining how security is enforced within the application. It's annotated with `@Configuration` to indicate that it's a source of bean definitions and `@EnableMethodSecurity` to enable Spring Security's method-level security annotations.

## Annotations

*   **`@Configuration`**: Marks this class as a source of bean definitions for the Spring application context.
*   **`@EnableMethodSecurity`**: Enables Spring Security's pre/post annotations for method-level security, allowing fine-grained control over method execution based on authorization.

## Bean Definitions

### `passwordEncoder()`

```java
@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder();
}
```

This method defines a `PasswordEncoder` bean, specifically an instance of `BCryptPasswordEncoder`. BCrypt is a strong hashing algorithm designed to securely store passwords. This encoder will be used throughout the application for hashing user passwords before storing them and for verifying passwords during authentication.

### `authenticationManager()`

```java
@Bean
public AuthenticationManager authenticationManager() {
    return authentication -> authentication; // no-op manager since we're manually authenticating
}
```

This method provides a no-operation (no-op) `AuthenticationManager` bean. In this setup, the `AuthenticationManager` simply returns the provided `Authentication` object without performing any actual authentication logic. This is because the authentication process, particularly for JWT-based authentication, is handled manually by custom filters (`JwtAuthenticationFilter` and `JwtAuthorizationFilter`) rather than relying on Spring Security's default `AuthenticationManager` flow.

### `filterChain(HttpSecurity http, JwtUtil jwtUtil, UserServiceClient userServiceClient)`

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http,
                                       JwtUtil jwtUtil,
                                       UserServiceClient userServiceClient) throws Exception {

    http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(sm -> sm.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .addFilter(new JwtAuthenticationFilter(jwtUtil, userServiceClient))
            .addFilterAfter(new JwtAuthorizationFilter(jwtUtil), JwtAuthenticationFilter.class)
            .authorizeHttpRequests(auth -> auth
                    .requestMatchers("/auth/login").permitAll()
                    .anyRequest().authenticated()
            )
            .httpBasic(withDefaults());

    return http.build();
}
```

This is the core method for configuring the `SecurityFilterChain`, which defines how HTTP requests are secured. It takes an `HttpSecurity` object, `JwtUtil` (for JWT operations), and `UserServiceClient` (for user details) as dependencies.

Here's a breakdown of the configuration steps:

1.  **`csrf(csrf -> csrf.disable())`**:
    *   Disables Cross-Site Request Forgery (CSRF) protection. This is common for stateless REST APIs where tokens (like JWTs) are used for authentication instead of session cookies, making CSRF attacks less relevant.

2.  **`sessionManagement(sm -> sm.sessionCreationPolicy(SessionCreationPolicy.STATELESS))`**:
    *   Configures session management to be `STATELESS`. This means that the application will not create or use HTTP sessions to store user authentication or authorization information. Each request must carry its own authentication credentials (e.g., a JWT), which is typical for RESTful APIs.

3.  **`addFilter(new JwtAuthenticationFilter(jwtUtil, userServiceClient))`**:
    *   Adds a custom `JwtAuthenticationFilter` to the security filter chain. This filter is responsible for processing authentication requests (e.g., `/auth/login`), validating user credentials, and generating a JWT upon successful authentication. It's placed early in the filter chain to handle login attempts.

4.  **`addFilterAfter(new JwtAuthorizationFilter(jwtUtil), JwtAuthenticationFilter.class)`**:
    *   Adds a custom `JwtAuthorizationFilter` to the security filter chain, ensuring it runs *after* the `JwtAuthenticationFilter`. This filter intercepts subsequent requests (after login) that contain a JWT. It validates the JWT, extracts user information, and sets the authenticated user in the Spring Security context, thereby authorizing the request.

5.  **`authorizeHttpRequests(auth -> auth.requestMatchers("/auth/login").permitAll().anyRequest().authenticated())`**:
    *   Configures authorization rules for HTTP requests:
        *   **`.requestMatchers("/auth/login").permitAll()`**: Specifies that requests to the `/auth/login` endpoint should be permitted for all users, including unauthenticated ones. This is necessary for users to initiate the login process.
        *   **`.anyRequest().authenticated()`**: Dictates that all other requests (any request not matching `/auth/login`) must be authenticated. This means a valid JWT or other authentication credentials must be present for these requests to be processed.

6.  **`httpBasic(withDefaults())`**:
    *   Enables HTTP Basic authentication with default settings. While the primary authentication mechanism is JWT, this might serve as a fallback or for specific internal endpoints if needed, though it's often disabled in pure JWT-based services.

Finally, `return http.build();` constructs and returns the `SecurityFilterChain` based on the defined configurations.

## Conclusion

The `SecurityConfig` class effectively sets up a robust, stateless security mechanism for the authentication service using JWTs. It defines how passwords are encoded, integrates custom JWT authentication and authorization filters, and establishes clear rules for which endpoints require authentication.

### `JwtAuthenticationFilter.java` Documentation

This document provides a detailed overview of the `JwtAuthenticationFilter` class, its purpose, functionality, and how it integrates within the authentication process of the `auth_service`.

## Table of Contents
- [Overview](#overview-1)
- [Class Definition](#class-definition-1)
- [Constructor](#constructor-1)
- [Methods](#methods-1)
    - [attemptAuthentication](#attemptauthentication)
    - [successfulAuthentication](#successfulauthentication)
- [Dependencies](#dependencies-1)
- [Usage](#usage-1)

## Overview

The `JwtAuthenticationFilter` is a core component of the authentication mechanism in the `auth_service`. It extends Spring Security's `UsernamePasswordAuthenticationFilter` to intercept login requests, validate user credentials, and upon successful authentication, generate and issue a JSON Web Token (JWT). This filter is responsible for handling the `/auth/login` endpoint.

## Class Definition

```java
public class JwtAuthenticationFilter extends UsernamePasswordAuthenticationFilter
```

The `JwtAuthenticationFilter` class extends `UsernamePasswordAuthenticationFilter`, which is a standard Spring Security filter for processing username and password authentication. This extension allows for customization of the authentication process, specifically to integrate JWT generation and user validation via a microservice.

## Constructor

```java
public JwtAuthenticationFilter(JwtUtil jwtUtil, UserServiceClient userServiceClient)
```

-   **`jwtUtil`**: An instance of `JwtUtil` used for generating JWTs. This utility class encapsulates the logic for creating signed JWTs with user details and roles.
-   **`userServiceClient`**: An instance of `UserServiceClient` responsible for communicating with the user service to validate user credentials. This promotes a microservice architecture where user management is decoupled from the authentication service.

The constructor also sets the `filterProcessesUrl` to `/auth/login`, indicating that this filter will intercept requests made to this specific endpoint for authentication attempts.

## Methods

### `attemptAuthentication`

```java
@Override
public Authentication attemptAuthentication(HttpServletRequest req, HttpServletResponse res) throws AuthenticationException, IOException
```

This method is overridden from `UsernamePasswordAuthenticationFilter` and is the entry point for processing an authentication attempt.

1.  **Request Body Parsing**: It reads the `HttpServletRequest`'s input stream to extract login credentials (username and password) from the request body. These credentials are deserialized into a `LoginRequest` object using `ObjectMapper`.
2.  **User Validation**: The `userServiceClient.validateUser(creds)` method is called to validate the provided credentials against the user service. This external call ensures that user authentication logic resides within the dedicated user service.
3.  **Authentication Object Creation**:
    *   If the `UserValidationResponse` indicates a valid user, the user's roles are converted into a list of `SimpleGrantedAuthority` objects.
    *   A `UsernamePasswordAuthenticationToken` is then created with the validated username, a `null` password (as the password has already been validated by the user service), and the granted authorities. This token represents a successfully authenticated user.
4.  **Error Handling**:
    *   If the `UserValidationResponse` is `null` or indicates an invalid user, a `BadCredentialsException` is thrown, signaling an authentication failure.
    *   `IOException` during request body parsing is wrapped in a `RuntimeException`.

### `successfulAuthentication`

```java
@Override
protected void successfulAuthentication(HttpServletRequest req,
                                        HttpServletResponse res,
                                        FilterChain chain,
                                        Authentication auth) throws IOException, ServletException
```

This method is invoked by Spring Security after a successful authentication attempt (i.e., `attemptAuthentication` returns a valid `Authentication` object).

1.  **Extract User Details**: It retrieves the authenticated username and their roles from the `Authentication` object.
2.  **JWT Generation**: The `jwtUtil.generateToken(username, roles)` method is called to create a new JWT. This token contains the user's identity and roles, which can be used for subsequent authorization checks.
3.  **Add JWT to Response Header**: The generated JWT is added to the `Authorization` header of the `HttpServletResponse` in the format `Bearer <token>`.
4.  **Respond with JWT in Body**: The response's content type is set to `application/json`, and the JWT is also written to the response body as a JSON object: `{"token": "<jwt_token>"}`. This provides the client with the token for future authenticated requests.

## Dependencies

-   **`com.example.auth_service.dto.LoginRequest`**: Data Transfer Object for login requests.
-   **`com.example.auth_service.dto.UserValidationResponse`**: Data Transfer Object for user validation responses from the user service.
-   **`com.example.auth_service.service.UserServiceClient`**: Feign client or similar for inter-service communication with the user service.
-   **`com.example.auth_service.security.JwtUtil`**: Utility class for JWT creation and validation.
-   **`com.fasterxml.jackson.databind.ObjectMapper`**: Used for JSON serialization and deserialization.
-   **Spring Security Classes**:
    -   `org.springframework.security.authentication.UsernamePasswordAuthenticationFilter`
    -   `org.springframework.security.authentication.BadCredentialsException`
    -   `org.springframework.security.authentication.UsernamePasswordAuthenticationToken`
    -   `org.springframework.security.core.Authentication`
    -   `org.springframework.security.core.authority.SimpleGrantedAuthority`
-   **Jakarta Servlet API**:
    -   `jakarta.servlet.FilterChain`
    -   `jakarta.servlet.ServletException`
    -   `jakarta.servlet.http.HttpServletRequest`
    -   `jakarta.servlet.http.HttpServletResponse`

## Usage

To integrate `JwtAuthenticationFilter` into a Spring Security configuration, it typically needs to be registered within the `SecurityFilterChain`. An example of how this might be done in a `SecurityConfig` class:

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Autowired
    private JwtUtil jwtUtil;

    @Autowired
    private UserServiceClient userServiceClient;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(AbstractHttpConfigurer::disable)
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/auth/login").permitAll()
                .anyRequest().authenticated()
            )
            .addFilter(new JwtAuthenticationFilter(jwtUtil, userServiceClient)) // Register the filter
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS));

        return http.build();
    }

    // Other necessary beans like AuthenticationManager, PasswordEncoder, etc.
}
```

This configuration ensures that:
-   CSRF protection is disabled (common for stateless APIs using JWTs).
-   The `/auth/login` endpoint is publicly accessible.
-   All other requests require authentication.
-   The `JwtAuthenticationFilter` is added to the filter chain.
-   Session management is set to `STATELESS`, as JWTs provide stateless authentication.

### `JwtUtil.java` Documentation

## Overview

The `JwtUtil` class is a Spring `@Component` responsible for generating and validating JSON Web Tokens (JWTs) within the authentication service. It leverages the `io.jsonwebtoken` library to perform cryptographic operations related to JWTs, ensuring secure communication and authentication.

## Dependencies

This class relies on the following key libraries:

*   **`io.jsonwebtoken.*`**: The core library for JWT creation, parsing, and validation.
*   **`org.springframework.beans.factory.annotation.Value`**: Used for injecting configuration properties from `application.properties` or `application.yml`.
*   **`org.springframework.stereotype.Component`**: Marks this class as a Spring component, making it eligible for auto-detection and dependency injection.

## Configuration Properties

The `JwtUtil` class uses two configuration properties, injected via `@Value` annotations:

*   `secret`: A `String` representing the secret key used for signing and verifying JWTs. This key is crucial for the security of the tokens and should be kept confidential.
    *   **Source**: `${security.jwt.secret-key}`
*   `expirationMs`: A `Long` representing the expiration time for JWTs in milliseconds.
    *   **Source**: `${security.jwt.expiration-ms}`

## Methods

### `generateToken(String username, Set<String> roles)`

Generates a new JWT for a given username and a set of roles.

*   **Purpose**: To create a signed JWT that can be used for authenticating a user and carrying their authorization roles.
*   **Parameters**:
    *   `username` (String): The principal (subject) of the token, typically the user's unique identifier.
    *   `roles` (Set<String>): A collection of roles or authorities associated with the user. These roles are included as a custom claim in the JWT.
*   **Returns**: `String` - The compact, URL-safe JWT string.
*   **Details**:
    The token is constructed using the `Jwts.builder()` fluent API. It sets the following claims:
    *   **Subject**: The provided `username`.
    *   **Custom Claim (`"roles"`)**: The `Set<String>` of roles.
    *   **Issued At**: The current date and time when the token is generated.
    *   **Expiration**: A future date and time calculated by adding `expirationMs` to the current time.
    *   **Signature**: The token is signed using the `HS256` (HMAC SHA-256) algorithm with the configured `secret` key.

### `validateToken(String token)`

Validates a given JWT string using the configured secret key.

*   **Purpose**: To verify the authenticity and integrity of a received JWT, ensuring it has not been tampered with and is signed by the expected issuer. It also implicitly checks for token expiration.
*   **Parameters**:
    *   `token` (String): The JWT string to be validated.
*   **Returns**: `Jws<Claims>` - A Java Web Signature object containing the parsed claims if the token is valid.
*   **Throws**:
    *   `io.jsonwebtoken.SignatureException`: If the token's signature is invalid.
    *   `io.jsonwebtoken.ExpiredJwtException`: If the token has expired.
    *   `io.jsonwebtoken.MalformedJwtException`: If the token is not a valid JWT.
    *   `io.jsonwebtoken.UnsupportedJwtException`: If the token is not supported.
    *   `java.lang.IllegalArgumentException`: If the token is null or empty.
*   **Details**:
    The method uses `Jwts.parser()` to create a parser instance, sets the signing key with the `secret`, and then attempts to parse the claims JWS (JSON Web Signature). If the token is valid and its signature matches the secret, a `Jws<Claims>` object is returned, allowing access to the token's header, claims, and signature.

## Usage Example (Conceptual)

```java
// In an authentication service or controller
@Service
public class AuthService {

    @Autowired
    private JwtUtil jwtUtil;

    public String login(String username, String password) {
        // ... authenticate user ...
        if (authenticationSuccessful) {
            Set<String> roles = new HashSet<>(Arrays.asList("USER", "ADMIN")); // Example roles
            return jwtUtil.generateToken(username, roles);
        }
        return null; // Or throw an exception
    }

    public boolean authorize(String jwtToken) {
        try {
            Jws<Claims> claims = jwtUtil.validateToken(jwtToken);
            // Access claims, e.g., claims.getBody().getSubject() or claims.getBody().get("roles")
            return true; // Token is valid
        } catch (Exception e) {
            // Log exception, token is invalid or expired
            return false;
        }
    }
}
```

## Security Considerations

The `secret` key used for signing JWTs is paramount to the security of the authentication system. It must be:

*   **Strong**: A long, random, and complex string.
*   **Confidential**: Never exposed in client-side code, logs, or version control.
*   **Securely Stored**: Ideally, retrieved from environment variables or a secure vault service in production environments.

---

## DTOs

### `UserValidationResponse` DTO

## Overview

The `UserValidationResponse` class is a Data Transfer Object (DTO) located in the `com.example.auth_service.dto` package. It is designed to encapsulate the outcome of a user validation process within the authentication service. This DTO provides a structured way to communicate whether a user is valid, their username, and the set of roles assigned to them.

## Class Definition

```java
package com.example.auth_service.dto;

import java.util.Set;

public class UserValidationResponse {

    private boolean valid;
    private String username;
    private Set<String> roles;

    // Getters and Setters
}
```

## Fields

This DTO contains the following private fields:

*   ### `valid`
    *   **Type**: `boolean`
    *   **Description**: A boolean flag indicating whether the user validation was successful. `true` if the user is valid, `false` otherwise.

*   ### `username`
    *   **Type**: `String`
    *   **Description**: The username of the validated user. This field will typically be populated if `valid` is `true`.

*   ### `roles`
    *   **Type**: `Set<String>`
    *   **Description**: A set of strings representing the roles assigned to the validated user. This field provides information about the user's permissions or group memberships.

## Getters and Setters

The class provides standard public getter and setter methods for each of its private fields, allowing for encapsulation and controlled access to the DTO's properties:

*   `isValid()`: Returns the value of the `valid` field.
*   `setValid(boolean valid)`: Sets the value of the `valid` field.
*   `getUsername()`: Returns the value of the `username` field.
*   `setUsername(String username)`: Sets the value of the `username` field.
*   `getRoles()`: Returns the value of the `roles` field.
*   `setRoles(Set<String> roles)`: Sets the value of the `roles` field.

## Usage

The `UserValidationResponse` DTO is primarily used as a return type for methods that perform user authentication or authorization checks. For instance, after an authentication attempt, a service layer might construct an instance of this DTO to convey the result back to a controller or another service.

**Example Scenario:**

A method in an authentication service might look like this:

```java
public UserValidationResponse validateUserCredentials(String username, String password) {
    UserValidationResponse response = new UserValidationResponse();
    // ... logic to validate username and password ...

    if (credentialsAreValid) {
        response.setValid(true);
        response.setUsername(username);
        response.setRoles(userRolesFromDatabase); // e.g., Set.of("ADMIN", "USER")
    } else {
        response.setValid(false);
        // username and roles might be null or empty if validation fails
    }
    return response;
}
```

This DTO ensures a consistent and clear structure for conveying user validation results across different layers of the application.

### `LoginRequest.java`

## Overview

The `LoginRequest` class is a simple Data Transfer Object (DTO) located in the `com.example.auth_service.dto` package. It is designed to encapsulate the necessary information for a user login request within the authentication service. This class serves as a structured format for receiving user credentials (username and password) from client applications.

## Purpose

This DTO's primary purpose is to facilitate the secure and organized transfer of login credentials from the client to the server-side authentication logic. By using a dedicated object, it ensures that login requests are well-defined, making API interactions clearer and less error-prone.

## Class Structure

```java
package com.example.auth_service.dto;

public class LoginRequest {

    private String username;
    private String password;

    // Getters and Setters would typically be here
    // public String getUsername() { return username; }
    // public void setUsername(String username) { this.username = username; }
    // public String getPassword() { return password; }
    // public void setPassword(String password) { this.password = password; }
}
```

### Fields

The `LoginRequest` class contains the following private fields:

*   **`username`**:
    *   **Type**: `String`
    *   **Description**: Represents the user's unique identifier or username used for authentication.
*   **`password`**:
    *   **Type**: `String`
    *   **Description**: Represents the user's password. This should be handled securely (e.g., transmitted over HTTPS and never logged in plain text).

## Usage

Typically, an instance of `LoginRequest` would be used as the request body in a RESTful API endpoint responsible for user authentication. For example, a Spring Boot controller might receive this object:

```java
// Example (not part of the provided file, for illustration)
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @PostMapping("/login")
    public ResponseEntity<?> authenticateUser(@RequestBody LoginRequest loginRequest) {
        // Process loginRequest.getUsername() and loginRequest.getPassword()
        // ...
        return ResponseEntity.ok("Login successful");
    }
}
```

In this scenario, the client would send a JSON payload similar to this:

```json
{
    "username": "user123",
    "password": "securepassword"
}
```

This JSON would then be automatically mapped to an instance of the `LoginRequest` class by frameworks like Spring Boot, allowing easy access to the submitted credentials.

## Considerations

*   **Security**: While this DTO holds sensitive information, the security of login credentials primarily depends on the transport layer (HTTPS), server-side validation, and secure password storage practices (e.g., hashing and salting).
*   **Immutability**: For enhanced safety and to prevent accidental modification after creation, consider making this DTO immutable by using a constructor to set all fields and omitting setters, especially if using a library like Lombok.
*   **Validation**: In a real-world application, it's crucial to add validation annotations (e.g., `@NotNull`, `@Size`) to the fields to ensure that the received data meets the required criteria before processing.

---

## Exceptions

No documentation snippets were provided for the Exceptions layer.

---

## Application Entrypoint

### AuthServiceApplication.java

This file serves as the entry point for the `auth-service` Spring Boot application. It initializes and runs the Spring application context, making it the core class for starting the authentication service.

## Package

`com.example.auth_service`

## Overview

The `AuthServiceApplication` class is a standard Spring Boot application class. It is responsible for bootstrapping the Spring application, enabling auto-configuration, component scanning, and other Spring Boot features.

## Class: `AuthServiceApplication`

```java
@SpringBootApplication
public class AuthServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(AuthServiceApplication.class, args);
    }

}
```

### `@SpringBootApplication` Annotation

The `@SpringBootApplication` annotation is a convenience annotation that combines three commonly used Spring Boot annotations:

1.  **`@Configuration`**: Tags the class as a source of bean definitions for the application context.
2.  **`@EnableAutoConfiguration`**: Tells Spring Boot to start adding beans based on classpath settings, other beans, and various property settings. For example, if `spring-webmvc` is on the classpath, this annotation flags the application as a web application and sets up a DispatcherServlet.
3.  **`@ComponentScan`**: Tells Spring to look for other components, configurations, and services in the `com.example.auth_service` package, allowing it to find and register controllers, services, repositories, and other custom components.

### `main` Method

The `main` method is the standard entry point for any Java application. In a Spring Boot application, this method uses `SpringApplication.run()` to launch the application.

*   **`SpringApplication.run(AuthServiceApplication.class, args);`**: This static method from `SpringApplication` is responsible for:
    *   Creating an appropriate `ApplicationContext` instance.
    *   Registering the `AuthServiceApplication` class as a configuration source.
    *   Performing a refresh of the context, which includes scanning for components, wiring up dependencies, and starting embedded servers (like Tomcat, if it's a web application).
    *   Running any `CommandLineRunner` or `ApplicationRunner` beans defined in the application.

## How to Run

To run this Spring Boot application, you can execute the `main` method directly from your IDE, or build a JAR file and run it from the command line:

```bash
# Build the application (e.g., using Maven or Gradle)
mvn clean package

# Run the JAR file
java -jar target/auth-service-0.0.1-SNAPSHOT.jar
```

---

## Tests

### `AuthServiceApplicationTests.java`

This file contains the primary test class for the `auth_service` application, designed to ensure that the Spring Boot application context loads correctly. It serves as a basic integration test to verify the foundational setup of the service.

## Class: `AuthServiceApplicationTests`

```java
@SpringBootTest
class AuthServiceApplicationTests {
    // ...
}
```

-   **Purpose**: This class is a standard Spring Boot test class responsible for loading the application context and verifying its integrity. The `@SpringBootTest` annotation tells Spring Boot to look for a main configuration class (for example, one with `@SpringBootApplication`) and use it to start a Spring application context.
-   **Annotations**:
    -   `@SpringBootTest`: This annotation is crucial for Spring Boot integration tests. It provides a convenient way to start up an application context, making all the components and configurations available for testing. It effectively launches the entire Spring application for the test.

## Method: `contextLoads()`

```java
@Test
void contextLoads() {
}
```

-   **Purpose**: This method is a simple test case to confirm that the Spring application context can load without throwing any exceptions. An empty method body is common for this type of test, as the success of the test is determined solely by the application context successfully starting up. If the context fails to load (e.g., due to misconfigurations, missing beans, or dependency issues), this test will fail.
-   **Annotations**:
    -   `@Test`: This annotation from JUnit 5 marks `contextLoads()` as a test method that should be executed by the test runner.

## Usage and Purpose

The `AuthServiceApplicationTests` class is a fundamental part of the `auth_service`'s testing suite. Its primary role is to act as a health check for the application's configuration. By successfully running this test, developers can be confident that:

1.  The Spring Boot application can start up correctly.
2.  All necessary beans are configured and can be initialized.
3.  There are no critical errors in the application's startup sequence.

While this test does not assert specific business logic, it is an essential first step in ensuring the overall stability and correct setup of the `auth_service` application.