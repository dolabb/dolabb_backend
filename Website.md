Website

1.Authentication & User Management:

1.1User Registration (Signup) Users can create accounts with phone number,email,
full name, and password. { "phone": "string", "email": "string", "fullName":
"string", "password": "string", "confirmPassword": "string", "countryCode":
"string", "dialCode": "string" "profileImage": "file" // optional "otp":Number 4
digit } Response: { "success": true, "user": { "id": "string", "username":
"string", "email": "string", "phone": "string", "profileImage": "string" }, otp:
"number sent to email for verification", "token": "string" } **Status Codes:**
200 (Success), 400 (Validation Error), 409 (User Exists), 500 (Server Error)

1.2.User Login Users can log in with email/username and password. { "email":
"string",  
 "password": "string" } Response: { "success": true, "user": { /_ user object _/
}, "token": "string" } **Status Codes:** 200 (Success), 401 (Unauthorized), 500 (Server
Error)

1.3.Forgot Password Users can request password reset via email otp 4 digit by
using. { "email": "string" }

**Response:** ```json { "success": true, "message": "Reset otp sent to email",
"otp": Number, } **Status Codes:** 200 (Success), 404 (User Not Found), 500
(Server Error)

4.New Password: { "otp": Number 4 digit geted in email, "newPassword": "string",
"confirmPassword": "string" } **Response:** ```json { "success": true,
"message": "Password reset successfully" }

**Status Codes:** 200 (Success), 400 (Invalid Token), 500 (Server Error)

2.User Profile Management

2.1.Get Profile: Users can view and edit their profile information. { "id":
"string", "username": "string", "email": "string", "phone": "string",
"fullName": "string", "profileImage": "string", "bio": "string", "location":
"string", "joinedDate": "string" "role": "string" // seller, buyer }

    2.2.Update Profile:

Users can update their profile information. { "username": "string", "fullName":
"string", "bio": "string", "location": "string", "profileImage": "string" }
Response: { "success": true, "user": { /_ updated user object _/ } } **Status
Codes:** 200 (Success), 400 (Validation Error), 500 (Server Error)

3.Product Management Users can browse products with filtering, sorting, and
pagination. 3.1.Get Products: **Query Parameters:** - `category`: string
(optional) - `subcategory`: string (optional) - `brand`: string (optional) -
`minPrice`: number (optional) - `maxPrice`: number (optional) - `size`: string
(optional) - `condition`: string (optional) // new, like-new, good, fair -
`onSale`: boolean (optional) - `sortBy`: string (optional) // relevance, price,
newest - `page`: number (optional, default: 1) - `limit`: number (optional,
default: 20) - `search`: string (optional)

    **Response:**
    ```json
    {
      "products": [
        {
          "id": "string",
          "title": "string",
          "description": "string",
          "price": "number",
          "originalPrice": "number",
          "images": ["string"],
          "category": "string",
          "subcategory": "string",
          "brand": "string",
          "size": "string",
          "color": "string",
          "condition": "string",
          "seller": {
            "id": "string",
            "username": "string",
            "profileImage": "string"
          },
          "isSaved": "boolean",
          "createdAt": "string"
        }
      ],
      "pagination": {
        "currentPage": "number",
        "totalPages": "number",
        "totalItems": "number",
        "itemsPerPage": "number"
      }
    }
    ```
    **Status Codes:** 200 (Success), 500 (Server Error)

3.2. Product Details:

Users can view detailed information about a specific product. GET
/api/products/:id`

- **Response:**

  ```json
  {
    "id": "string",
    "title": "string",
    "description": "string",
    "price": "number",
    "originalPrice": "number",
    "images": ["string"],
    "category": "string",
    "subcategory": "string",
    "brand": "string",
    "size": "string",
    "color": "string",
    "condition": "string",
    "tags": ["string"],
    "seller": {
      "id": "string",
      "username": "string",
      "profileImage": "string",
      "rating": "number",
      "totalSales": "number"
    },
    "likes": "number",
    "isLiked": "boolean",
    "isSaved": "boolean",
    "shippingInfo": {
      "cost": "number",
      "estimatedDays": "number",
      "locations": ["string"]
    },
    "createdAt": "string",
    "affiliateCode": "string" // if seller is affiliate
  }
  ```

  **Status Codes:** 200 (Success), 404 (Not Found), 500 (Server Error)

  3.3. Save/Unsave Product: List Product (Seller) can save/unsave products to
  their wishlist. { "productId": "string" }

- **Status Codes:** 201 (Created), 400 (Validation Error), 401 (Unauthorized),
  500 (Server Error)

  3.4.Create Product: { "itemtitle": "string", "description": "string", "price":
  "number", "currency": "string", "Quantity": "number", "Gender": "string",
  "Size":, "string", "Condition": "string", "SKU/ID (Optional)": "string",
  "Tags/Keywords": ["string"], "Images": ["file"], // multiple images "Shipping
  Cost": "number", "Processing Time (days)": "number", "category": "selected
  from predefined list", "Affiliate Code (Optional)": "string" // optional }

category list: women, men,watches,jawelry,accessories will use everywhere it
need for category field of product

**Response:** ```json { "success": true, "product": { /_ product object _/ } }
**Status Codes:** 201 (Created), 400 (Validation Error), 401 (Unauthorized), 500
(Server Error) 3.5.Get All Product By Seller ID: Seller can view all products
listed by a himself.: GET /api/sellers/:sellerId/products

- **Response:**
  ```json
  {
    "products": [
      {
      object of products
      }
    ]
  }
  ```
  **Status Codes:** 200 (Success), 404 (Not Found), 500 (Server Error)

3.6.Delete,Update Product:

4.Save/Unsave Product: List Product (Seller/buyer) can save/unsave products to
their wishlist. `POST /api/products/:id/save`

- **Response:**
  ```json
  {
    "success": true,
    "isSaved": "boolean"
  }
  ```
- `DELETE /api/products/:id/save`

  - **Response:** `json { "success": true, "isSaved": false } `

        4.1:Featured Products

    **Query Parameters:** - `limit`: number (optional, default: 10)

  - **Response:**
    ```json
    {
      "products": [
        /* array of product objects */
      ]
    }
    ```

pagination should be there also
``` 4.2:Trending Products: GET /api/products/trending`

- **Query Parameters:**
  - `limit`: number (optional, default: 10)
- **Response:** `json { "products": [ /* array of product objects */ ] } `
  pagination should be there also

Make Offers on Products: Users can make offers on products. on product detail
page there are 2 buttons one is ask question from the seller who listed that
product another is make offer buyer can make offer on that product and it will
be below then the product price or equal to product price when buyer click on
make offer button a popup will open with input field to enter offer amount and a
submit button { "productId": "string", "offerAmount": "number" } Response: {
"success": true, "offer": { "id": "string", "productId": "string", "buyerId":
"string", "offerAmount": "number", "status": "string", // pending, accepted,
rejected "createdAt": "string" } } **Status Codes:** 201 (Created), 400
(Validation Error), 401 (Unauthorized), 500 (Server Error)

Chat System Explanation: How It Works for Buyers and Sellers: The chat system
allows buyers and sellers to communicate about products, negotiate offers, and
manage transactions. The system combines traditional messaging with integrated
offer management, creating a seamless experience for marketplace interactions.
**Query Parameters:** - `userId`: string (optional) // get conversation with
specific user 1.1Conversations List: Shows all conversations with other users

- Displays:

  - User avatar
  - Username (@username)
  - Last message preview
  - Timestamp (e.g., "2h ago")
  - Unread message count badge

  1.2:Chat Area (Center) Chat header with user info and "Active now" status

  - Messages (both text and offers)
  - Message input area

  2.How It Works for Buyers Buyers can start conversations with sellers about
  products

  - Can be initiated from:
    - Product detail pages ("Contact Seller" button or make an offer button that
      offer will appears in both chat as in above current offer and offer make)

  2.1:See all conversations with sellers

  - Conversations are sorted by most recent activity
  - Unread messages are highlighted with a badge

  2.2:Type text messages

  - Attach images (product photos, questions, etc.)
  - Timestamp shows when message was sent

3. **Making Offers** 3.1:Buyers can make offers on products through the chat
   - Offers appear as special message cards in the conversation
   - Offer cards show:
     - Product name
     - Original price
     - Offer price
     - Shipping cost
     - Expiration date
   - Offers are marked as "Your Offer" 3.2:Receiving Offer Responses\* When
     seller accepts/rejects/counters an offer, it appears in chat
   - Can accept seller's counter-offers
   - Can proceed to checkout directly from accepted offers

3.3:Offer Actions (When Receiving Offers)\*\*

- **Accept:** Redirects to checkout with offer details
- **Counter:** Create a counter-offer with different price
- **Reject:** Decline the offer (if implemented)

4.How It Works for Sellers 4.1:**Receiving Messages**

- Sellers receive messages from buyers interested in their products
- Conversations appear in the same list format
- Unread messages are highlighted

4.2:**Responding to Buyers**

- Can reply to buyer questions
- Can send product images or additional information 4.3:**Receiving Offers**
- When buyers make offers, they appear as special cards in chat

  - Offer cards show:
    - Product name
    - Original price
    - Buyer's offer price
    - Shipping cost
    - Expiration date
  - Offers are marked as "Offer Received" 4.4:**Managing Offers** **Accept
    Offer:**

         - Click "Accept" button
         - Creates order/checkout link for buyer
         - Offer status changes to "accepted"

  **Counter Offer:**

       - Click "Counter" button
       - Enter new price
       - Send counter-offer back to buyer
       - Creates new offer card in conversation

  **Reject Offer:** - Decline the offer (if implemented) - Offer status changes
  to "rejected"

**Product Context**

- Conversations are typically linked to specific products
- Can reference product details in messages
- Offers are product-specific

5.Message Flow Example

### Scenario: Buyer wants to negotiate price

**Buyer initiates:**

```
Buyer: "Hello! Is this item still available?"
```

**Seller responds:**

```
Seller: "Yes, it is available!"
```

**Buyer makes offer:**

```
[Offer Card Appears]
Product: Vintage Denim Jacket
Original Price: SAR 13
Your Offer: SAR 9
Shipping: SAR 1
Expires: 10 Feb 2025
```

**Seller counters:**

```
[Counter Offer Card Appears]
Product: Vintage Denim Jacket
Original Price: SAR 13
Counter Offer: SAR 11
Shipping: SAR 1
Expires: 12 Feb 2025
```

**Buyer accepts:**

```
Buyer: "Sounds good! I'll take it."
[Clicks Accept on counter-offer]
→ Redirects to checkout
```

6.Key Features:

- Real-time Messaging
- Text messages with timestamps
- Image attachments
- Offers appear inline with messages
- Image upload support
- Multiple images per message
- Unread message count badges

**Message Structure:**

interface Message { id: string; text: string; sender: 'me' | 'other'; timestamp:
string; attachments?: string[]; }

**Offer Structure:** interface Offer { id: string; type: 'your-offer' |
'offer-received'; product: string; size: string; price: number; offer: number;
shipping: number; expires: string; }

````

7.Required Backend APIs
1.**Get Conversations**
2. **Get Conversation Messages**
3. **Send Message**
4. **Upload File**
5.**Offer Management**
POST /api/offers - Create offer
GET /api/offers - Get offers
PUT /api/offers/:id/accept - Accept offer
PUT /api/offers/:id/reject - Reject offer
POST /api/offers/:id/counter - Counter offer



8.User Roles & Permissions

### Both Buyers and Sellers:

- ✅ Can send/receive messages
- ✅ Can view conversations
- ✅ Can attach images
- ✅ Can see offer cards

### Buyers Only:

- ✅ Can make offers on products
- ✅ Can accept counter-offers
- ✅ Can proceed to checkout from offers

### Sellers Only:

- ✅ Can accept/reject/counter offers
- ✅ Can create checkout links for accepted offers







9.Checkout
  {
      "offerId": "string", // if checkout from offer
      "cartItems": ["string"], // if checkout from cart
      "deliveryAddress": {
        "fullName": "string",
        "phone": "string",
        "address": "string",
        "city": "string",
        "postalCode": "string",
        "country": "string",
        "additionalInfo": "string"
      }
    }
    ```
  - **Response:**
    ```json
    {
      "success": true,
      "orderId": "string",
      "checkoutData": {
        "product": "string",
        "size": "string",
        "price": "number",
        "offerPrice": "number",
        "shipping": "number",
        "total": "number"
      }
    }
    ```

9.1:Payment Processing

**Feature Description:** Process payments using Moyasar payment gateway.

**Required APIs:**

- `POST /api/payment/process`
  - **Request Body:**
    ```json
    {
      "tokenId": "string", // optional, if using saved card
      "cardDetails": {
        "name": "string",
        "number": "string",
        "month": "string",
        "year": "string",
        "cvc": "string"
      },
      "amount": "number",
      "description": "string",
      "metadata": {
        "locale": "string",
        "offerId": "string",
        "product": "string",
        "size": "string",
        "price": "number",
        "offerPrice": "number",
        "shipping": "number"
      }
    }
    ```
  - **Response:**
    ```json
    {
      "success": true,
      "payment": {
        "id": "string",
        "status": "string",
        "amount": "number",
        "currency": "string",
        "source": {
          /* payment source object */
        }
          "order": {
        /* order object */
      }
      }
    }
    ```
  - **External API:** Moyasar Payment Gateway
    - **Endpoint:** `https://api.moyasar.com/v1/payments`
    - **Method:** POST



My Store (Seller Dashboard)

**Feature Description:** Sellers can manage their listed products and view
payments.

**Required APIs:**

- `GET /api/user/products`
  - **Query Parameters:**
    - `status`: string (optional) // active, sold, draft
    - `page`: number (optional)
    - `limit`: number (optional)
  - **Response:**
    ```json
    {
      "products": [
        /* array of product objects */
      ],
      "pagination": {
        /* pagination object */
      }
    }
    ```
- `GET /api/user/payments`
  - **Query Parameters:**
    - `status`: string (optional) // ready, shipped, delivered
    - `page`: number (optional)
  - **Response:**
    ```json
    {
      "payments": [
        {
          "id": "string",
          "product": {
            /* product object */
          },
          "buyer": {
            /* user object */
          },
          "orderDate": "string",
          "status": "string",
          "totalPrice": "number",
          "shippingAddress": {
            /* address object */
          }
        }
      ]
    }
    ```
- `PUT /api/user/payments/:id/ship`
  - **Request Body:**
    ```json
    {
      "trackingNumber": "string"
    }
    ```
  - **Response:**
    ```json
    {
      "success": true,
      "payment": {
        /* updated payment object */
      }
    }
    ```

**Current Implementation:** My Store page exists, uses localStorage

---

### 7.2 Buyer Dashboard

**Feature Description:** Buyers can view their orders and manage offers.

**Required APIs:**

- `GET /api/user/orders` (same as GET /api/orders)
- `GET /api/user/offers` (same as GET /api/offers)

**Current Implementation:** Buyer dashboard exists with mock data

---

### Profile Management

**Feature Description:** Users can update their profile information.




Affiliate Program:

Affiliate Registration:
Users can register as affiliates with bank details
{
      "fullName": "string",
      "email": "string",
      "phone": "string",
      "password": "string",
      "countryCode": "string",
      "Phonnumber": "string",
      "bankName": "string",
      "accountNumber": "string",
      "iban": "string", // optional
      "accountHolderName": "string"
}
Response
{
  "success": true,
      "affiliate": {
        "id": "string",
        "fullName": "string",
        "email": "string",
        "phone": "string",
        "affiliateCode": "string", // e.g., "AFF-XXXXXX"
        "bankDetails": {
          /* bank details object */
        },
        "totalEarnings": "number",
        "totalCommissions": "number",
        "codeUsageCount": "number",
        "status": "string", // active, inactive
        "createdAt": "string"
      }
}


Affiliate Login:
Affiliates can log in to their website view.
  {
      "email": "string",
      "password": "string"
    }
Response:{
      "success": true,
      "affiliate": {
        /* affiliate object */
      },
      "token": "string"
    }

 Affiliate Code Validation:
 Validate affiliate codes when Affiliate registered.
         {
      "code": "string"
    }
    Response:
  {
      "valid": "boolean",
      "message": "string",
      "affiliate": {
        /* affiliate object */
      } // if valid how to check valid if he full fill all the requirements while registering
    }

    Affiliate Cashout:
    Affiliates can request cashout of their earnings from admin:
    Required APIs:
      {
      "affiliateId": "string",
      "amount": "number"
    }
    Response:
    {
      "success": true,
      "cashoutRequest": {
        "id": "string",
        "affiliateId": "string",
        "amount": "number",
        "status": "string", // pending, approved, rejected, completed
        "requestedAt": "string",
        "reviewedAt": "string",
        "reviewedBy": "string"
      }
    }



    overall features:
    Users can search for products.
````
