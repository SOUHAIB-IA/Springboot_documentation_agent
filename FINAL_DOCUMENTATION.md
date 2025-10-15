The `AuthServiceApplication` class is the entry point for the authentication service. It is a standard Spring Boot application that uses the `@SpringBootApplication` annotation to enable auto-configuration, component scanning, and other Spring Boot features.

The `main` method uses `SpringApplication.run()` to launch the application. This method bootstraps the application, creates the Spring application context, and starts the embedded web server (if applicable).

**Key Features:**

*   **`@SpringBootApplication`**: This annotation combines `@Configuration`, `@EnableAutoConfiguration`, and `@ComponentScan`.
    *   `@Configuration`: Tags the class as a source of bean definitions for the application context.
    *   `@EnableAutoConfiguration`: Tells Spring Boot to "guess" and configure beans based on classpath settings, other beans, and various property settings.
    *   `@ComponentScan`: Tells Spring to look for other components, configurations, and services in the `com.example.auth_service` package, allowing it to find and register controllers, services, and repositories.

**Usage:**

To run this application, execute the `main` method. This will start the Spring Boot application, making the authentication service available.

---

### ERROR: An unexpected error occurred in writer: 500 An internal error has occurred. Please retry or report in https://developers.generativeai.google/guide/troubleshooting. Skipping.

---

The `AuthController` class is a REST controller responsible for handling authentication-related requests within the `auth_service`. It is mapped to the `/auth` endpoint. Currently, the controller is empty and does not contain any authentication endpoints.

---

The `JwtAuthorizationFilter` class is a `OncePerRequestFilter` that intercepts incoming HTTP requests to authorize them based on a JSON Web Token (JWT) provided in the `Authorization` header.

**Dependencies:**

*   `jakarta.servlet.*`: For servlet-related functionalities like `HttpServletRequest`, `HttpServletResponse`, and `FilterChain`.
*   `io.jsonwebtoken.Claims`: To represent the claims (payload) of a JWT.
*   `org.springframework.security.authentication.*`: For authentication-related classes like `UsernamePasswordAuthenticationToken`.
*   `org.springframework.security.core.context.SecurityContextHolder`: To manage the security context.
*   `org.springframework.web.filter.OncePerRequestFilter`: Base class for filters that are guaranteed to be executed only once per request.

**Constructor:**

*   `JwtAuthorizationFilter(JwtUtil jwtUtil)`:
    *   Initializes the filter with a `JwtUtil` instance, which is responsible for JWT validation and parsing.

**`doFilterInternal` Method:**

*   `protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain chain) throws ServletException, IOException`:
    *   This method is the core of the filter, executed for every incoming request.
    *   It extracts the `Authorization` header from the request.
    *   If the header exists and starts with "Bearer ", it extracts the JWT token.
    *   It then attempts to validate the token using `jwtUtil.validateToken(token)`.
    *   If the token is valid, it extracts the subject (username) from the token's claims and creates a `UsernamePasswordAuthenticationToken`.
    *   This authentication token is then set in the `SecurityContextHolder`, effectively authenticating the user for the current request.
    *   If token validation fails (e.g., due to an expired or invalid token), the response status is set to `HttpServletResponse.SC_UNAUTHORIZED` (401), and the request processing is stopped.
    *   Finally, `chain.doFilter(req, res)` is called to pass the request to the next filter in the chain or to the target servlet.

**Purpose:**

This filter plays a crucial role in securing a Spring Boot application by:

1.  **Intercepting requests:** It acts as a gateway for incoming requests.
2.  **Validating JWTs:** It ensures that requests containing a JWT in the `Authorization` header have a valid and unexpired token.
3.  **Authenticating users:** Upon successful token validation, it authenticates the user by setting the authentication object in the Spring Security context.
4.  **Protecting resources:** By rejecting requests with invalid or missing JWTs, it prevents unauthorized access to protected resources.


---

The `SecurityConfig` class is a Spring Security configuration class that sets up the security filters, password encoder, and authentication manager for the application.

### `passwordEncoder()`

This method defines a `PasswordEncoder` bean that uses `BCryptPasswordEncoder` for hashing passwords.

### `authenticationManager()`

This method defines an `AuthenticationManager` bean. In this configuration, it's a no-op manager because authentication is handled manually by the `JwtAuthenticationFilter`.

### `filterChain(HttpSecurity http, JwtUtil jwtUtil, UserServiceClient userServiceClient)`

This method configures the `SecurityFilterChain`. It performs the following actions:

*   **Disables CSRF protection**: Since the application uses JWT for authentication, CSRF protection is not necessary.
*   **Sets session management to stateless**: This ensures that no session information is stored on the server, which is typical for JWT-based authentication.
*   **Adds `JwtAuthenticationFilter`**: This filter handles user login and generates a JWT upon successful authentication.
*   **Adds `JwtAuthorizationFilter`**: This filter authorizes requests by validating the JWT in the request header.
*   **Configures authorization rules**:
    *   `/auth/login` endpoint is accessible to all.
    *   All other requests require authentication.
*   **Enables HTTP Basic authentication**: This is configured with default settings.

This configuration ensures that all incoming requests are secured using JWT-based authentication and authorization.


---

The `JwtAuthenticationFilter` class extends `UsernamePasswordAuthenticationFilter` and is responsible for handling user authentication and JWT generation.

**Purpose:**
This filter intercepts login requests, validates user credentials by communicating with a `UserServiceClient`, and upon successful authentication, generates a JWT (JSON Web Token) which is then included in the response header and body.

**Constructor:**
* `JwtAuthenticationFilter(JwtUtil jwtUtil, UserServiceClient userServiceClient)`:
    * Initializes the filter with a `JwtUtil` instance for JWT operations and a `UserServiceClient` for user validation.
    * Sets the filter's processing URL to `/auth/login`.

**Methods:**

* `@Override public Authentication attemptAuthentication(HttpServletRequest req, HttpServletResponse res)`:
    * This method attempts to authenticate the user.
    * It reads `LoginRequest` credentials from the request input stream.
    * It calls `userServiceClient.validateUser()` to validate the provided credentials.
    * If the user is valid, it creates a `UsernamePasswordAuthenticationToken` with the username and user roles (as `SimpleGrantedAuthority` objects) and returns it.
    * If validation fails, it throws a `BadCredentialsException`.
    * It handles `IOException` during input stream reading by throwing a `RuntimeException`.

* `@Override protected void successfulAuthentication(HttpServletRequest req, HttpServletResponse res, FilterChain chain, Authentication auth) throws IOException, ServletException`:
    * This method is called upon successful user authentication.
    * It extracts the username and roles from the `Authentication` object.
    * It generates a JWT using `jwtUtil.generateToken()` with the username and roles.
    * It adds the generated JWT to the `Authorization` header of the response in the format "Bearer <token>".
    * It sets the response content type to `application/json`.
    * It writes a JSON object containing the generated token to the response body.

---

The `JwtUtil` class is a utility component for generating and validating JSON Web Tokens (JWTs). It uses a secret key and an expiration time, configured via Spring's `@Value` annotation, to perform these operations.

### Fields

*   `secret`: A `String` representing the secret key used for signing and verifying JWTs. This value is injected from the `security.jwt.secret-key` property in the application's configuration.
*   `expirationMs`: A `Long` representing the expiration time for JWTs in milliseconds. This value is injected from the `security.jwt.expiration-ms` property in the application's configuration.

### Methods

#### `generateToken(String username, Set<String> roles)`

This method generates a new JWT for a given username and a set of roles.

*   **Parameters:**
    *   `username`: A `String` representing the subject of the JWT (typically the user's identifier).
    *   `roles`: A `Set<String>` containing the roles or authorities associated with the user.
*   **Returns:**
    *   A `String` representing the generated JWT.
*   **Functionality:**
    1.  Sets the subject of the token to the provided `username`.
    2.  Adds a custom claim named "roles" with the provided `roles`.
    3.  Sets the issued at time to the current date.
    4.  Sets the expiration time based on the current time plus the configured `expirationMs`.
    5.  Signs the token using the `HS256` algorithm and the configured `secret`.
    6.  Compacts the JWT into its final string representation.

#### `validateToken(String token)`

This method validates a given JWT.

*   **Parameters:**
    *   `token`: A `String` representing the JWT to be validated.
*   **Returns:**
    *   A `Jws<Claims>` object containing the parsed claims if the token is valid.
*   **Throws:**
    *   Various `io.jsonwebtoken` exceptions (e.g., `SignatureException`, `ExpiredJwtException`, `MalformedJwtException`) if the token is invalid or has expired.
*   **Functionality:**
    1.  Parses the JWT using the configured `secret` to verify its signature and claims.
    2.  If the token is valid, it returns a `Jws<Claims>` object, allowing access to the token's header, claims, and signature.


---

The `UserValidationResponse` class is a Data Transfer Object (DTO) used to encapsulate the result of a user validation process. It provides information about whether a user is valid, their username, and their assigned roles.

### Fields:

*   `valid`: A `boolean` indicating whether the user is valid.
*   `username`: A `String` representing the username of the validated user.
*   `roles`: A `Set` of `String` objects, where each string represents a role assigned to the user.

### Methods:

*   `isValid()`: Returns a `boolean` indicating if the user is valid.
*   `setValid(boolean valid)`: Sets the validity status of the user.
*   `getUsername()`: Returns the username of the validated user.
*   `setUsername(String username)`: Sets the username of the user.
*   `getRoles()`: Returns the set of roles assigned to the user.
*   `setRoles(Set<String> roles)`: Sets the roles for the user.

---

The `LoginRequest` class is a Data Transfer Object (DTO) used to encapsulate the data required for a user login request. It typically contains the credentials provided by the user when attempting to authenticate.

### Fields:

*   **`username`**: A `String` representing the user's unique identifier, such as a username or email address, used for authentication.
*   **`password`**: A `String` representing the user's password, provided for verification during the login process.

---

The `AuthServiceApplicationTests` class is a test class for the `auth_service` application. It is annotated with `@SpringBootTest`, which indicates that it's a Spring Boot test and will load the full application context.

**Purpose:**
This class is responsible for ensuring that the Spring application context for the `auth_service` loads correctly.

**Methods:**

*   `contextLoads()`: This test method is a basic smoke test. Its primary purpose is to verify that the application context can be loaded without any errors. If the context loads successfully, it indicates that the application's basic configuration and dependencies are correctly set up.

**Usage:**
This test can be run as part of the build process to quickly identify any issues with the application's startup or configuration.