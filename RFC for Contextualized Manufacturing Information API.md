Smart Manufacturing API Working Group\
Request for Comments: 001\
Category: Informational\
September 26, 2024

# Common API for Contextualized Manufacturing Information (CMIAPI)

#### Status of this Memo

This memo provides information for the Smart Manufacturing/Industry 4.0 community. It proposes a set of common interfaces for programmatic access to contextualized manufacturing information that any information platform vendor can implement to support portable application development.

While this document follows Internet RFC style and conventions, and may refer to Internet RFCs, it is not intended for consideration by the IETF or IAB as the problem domain is specific to manufacturing information systems.

#### Draft Specific Comments

As an early RFC, the authors opted to remain silent on the style of interface implementation, although both REST and GraphQL are considerations for a future specification. As a result, specific implementation guidance cannot be included at this stage. Once a style is selected, future versions of this document will be updated with more implementation details.

#### Copyright Notice

Copyright (C) CESMII, the Smart Manufacturing Institute, 2024. All Rights Reserved.

## Abstract

This document provides a common API that any information platform vendor can implement on a server to abstract the vendor-specific implementations of data organization and contextualization into a set of programmer's interfaces that helps ensure applications written against one implementation can work against another. While informed by OPC UA's REST API, and designed to be implementable against that API, this API should be supportable on a wide variety of existing, and future, information platforms. This RFC pertains specifically to the requirements for server-side implementations, and does not specifically address client requirements (save for those that may be inferred from server functionality)

## 1. Introduction

Raw manufacturing data is rarely stored in a ready-to-consume fashion, with the best commonly implemented structure being key-value pairs, often available only through live sampling, but sometimes stored historically as time-series values with a timestamp attached. Any structure or organization more sophisticated is invariably a feature of a proprietary, vendor-specific implementation, or requires homogeneous adoption of a more modern protocol and a complementary vendor ecosystem, often augmented by non-standard, or internal-only practices for semantic and structural consistency.

Vendor-dependent, non-standard, or internal-only infrastructure prevents application portability across information infrastructure variations. The part of an information stack where information value is rendered is permanently tied to the platform it was initially built against. This state is similar to that of general computing in the early 1980s, in which operating system variations proliferated, breaking application portability. In that era, highly successful commercial efforts (such as Microsoft Windows) and standardization efforts (such as POSIX) eventually led to a finite, and tolerable number of platforms that application developers must support -- kicking off 3+ decades of rapid innovation, the likes of which have never been replicated in the manufacturing world.

This document defines an API that any modern platform provider can implement to abstract applications from the specifics of the platform implementation, and ensure a base-level of application portability and compatibility. As the first RFC in a series, this document does not specify the technologies to be used for the implementation of the API; rather it focuses on the capabilities and primitives necessary for an implementation. As a RFC, this document invites feedback and discussion from the manufacturing community.

Comparisons may be drawn to the OPC/UA REST API, which exposes OPC/UA Client-Server functionality over REST. This API is not intended to replace, or compete, with this functionality. Rather it proposes a complementary API for Information Platforms that typically sit above one or more OPC/UA servers, and provide data to applications that may come from multiple data sources.

Comparisons may also be drawn to the concept of a Unified Namespace (UNS), often implemented using one or more MQTT Brokers. This API is intended to complement a UNS architecture, providing a query layer that can provide application developers with an abstraction that can sit above one or more MQTT brokers, as well as other live and historical data sources.

Finally, comparisons may be drawn to commercial offerings that provide similar functionality. This is by design: this API proposes a common programmer's interface not tied to any specific vendor's implementation, but implementable by many to create compatibility in support of application portability. Platform vendors who wish to support this API MAY choose to implement the API along-side, or on top of, their own proprietary APIs.

## 2. Definitions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in Internet RFC 2119 [RFC2119].

Address Space   The complete collection of Contextualize Information that a platform makes available to clients
API		        Application Programming Interface
CMIAPI          Contextualized Manufacturing Information API
CMIP		        Contextualized Manufacturing Information Platform that supports the CMIAPI
Element		    Any object or object attribute persisted by a CMIP
ElementId	    A platform-specific, persistent and unique key for an Element
Control System  An electronic control system and associated instrumentation used for industrial process control

## 3. CMIAPI Basic Interfaces

The CMIAPI SHALL be implemented over HTTPS, and support the interfaces listed in this section. In order to properly support some of these interfaces, implementations MUST support the required capabilities listed in section 4, and MAY support the optional capabilities listed in section 4. 

### 3.1 Request and Response Structure

#### 3.1.1 Response Serialization

Implementations MUST support a default JSON serialization for all responses.

Implementations MAY support a Binary serialization for all responses, where the format of such response will be determined in a future RFC.

Implementations MAY support a HTML serialization for all responses, that proposes an embed-able UI for the response data (for example, HTMX). Such pre-rendered responses MAY include Hyperlinks to follow-up queries in the same format, facilitating progressive UI expansion.

#### 3.1.2 Request Headers

Applications consuming the API SHOULD use the normal "accept" and "content-type" headers for indicating inbound and outbound serialization format. If omitted, the default JSON serialization should be used.

### 3.2 Informative Interfaces

#### 3.2.1 LiveValue

When invoked as a Query, the LiveValue interface MUST return the current value available in the CMIP for the requested object, by ElementId.

When invoked as a Query, the LiveValue interface MAY support an array of requested object ElementIds to reduce round-trips where multiple values are required by an application, in which case, the return payload MUST be an array.

When invoked as a Query, if indicated by an optional query parameter, the response payload MUST include the following metadata about the returned value:
- ElementId: a unique identifier for that element following a documented notation or standard
- DataType: incudes most-derived Type name of an object, or primitive datatype for an attribute, and MUST use the JavaScript primitive types
- Quality: a data quality indicator following the standard established by the [OPC UA standard status codes](https://reference.opcfoundation.org/Core/Part8/v104/docs/A.3.2.3#_Ref377938607). If data quality is not available, the CMIP may return a GOOD status.
- TimeStamp: a timestamp corresponding to the time and date the data was recorded in the CMIP, following the standard established by [Internet RFC 3339](https://www.rfc-editor.org/rfc/rfc3339)

When invoked as a Query, if indicated by an optional query parameter, the response payload MAY include the following metadata about the returned value;
- Interpolation: if the element value is interpolated, rather than stored, indicate the interpolation method
- EngUnit: a string indicating the engineering unit for measuring the element value. Where present, the definitions found in UNECE Recommendation Number 20 MUST be used.
- NamespaceURI: if the element value is an object, a URI indicating the Namespace of the object MUST be returned. If the value is an attribute, a URI indicating the Namespace SHOULD be returned. If the Namespace is an implementation of standards-based definition that includes a URI, that URI MUST be used.
- ParentId: the ElementId of the parent object
- Attribute Metadata: Additional information about how an object attribute is stored or treated by the underlying platform.

When invoked as an Update, the LiveValue interface MUST accept a new current value for the requested object to be recorded in the CMIP, by ElementId. If the CMIP supports write-back to a Control System (for example, via an interface to a PLC) additional security requirements outside the scope of this proposal MUST be considered.) 

When invoked as an Update the LiveValue interface MAY accept an array of current values for an array of of ElementIds.

#### 3.2.2 HistoricalValue

When invoked as a Query, the HistoricalValue interface MUST return an array of historical values in a time range available in the contextualized information platform for the requested object, by ElementId.

When invoked as a Query, the HistoricalValue interface MAY support an array of requested object ElementIds to reduce round-trips where multiple values are required by an application, in which case, the return payload MUST be an array of arrays.

When invoked as a Query, if indicated by an optional query parameter, the response payload MUST include the following metadata about the returned value:
- ElementId: a unique identifier for that element following a documented notation or standard
- DataType: incudes most-derived Type name of an object, or primitive datatype for an attribute, and MUST use the JavaScript primitive types
- Quality: a data quality indicator following the standard established by the [OPC UA standard status codes](https://reference.opcfoundation.org/Core/Part8/v104/docs/A.3.2.3#_Ref377938607). If data quality is not available, the CMIP may return a GOOD status.
- TimeStamp: a timestamp corresponding to the time and date the data was recorded in the CMIP, following the standard established by [Internet RFC 3339](https://www.rfc-editor.org/rfc/rfc3339)

When invoked as a Query, if indicated by an optional query parameter, the response payload MAY include the following metadata about the returned value;
- Interpolation: if the element value is interpolated, rather than stored, indicate the interpolation method
- EngUnit: a string indicating the engineering unit for measuring the element value. Where present, the definitions found in [UNECE Recommendation Number 20]((https://unece.org/trade/documents/2021/06/uncefact-rec20-0)) MUST be used.
- NamespaceURI: if the element value is an object, a URI indicating the Namespace of the object MUST be returned. If the value is an attribute, a URI indicating the Namespace SHOULD be returned.
- ParentId: the ElementId of the parent object
- Attribute Metadata: Additional information about how an object attribute is stored or treated by the underlying platform.

When invoked as an Update, the HistoricalValue interface MUST accept an updated historical value for the requested object and timestamp, by ElementId.

When invoked as an Update, the HistoricalValue interface MAY accept an array of updated historical values for an array of specified objects and timestamps, by ElementId.

When invoked as a Put, the HistoricalValue interface MAY accept an array of new historical values for an array of specified objects and timestamps, by ElementId.

When updating Historical data, the CMIP SHOULD implement auditing or tracking of such changes.

### 3.3 Exploratory Interfaces

#### 3.3.1 Namespaces

When invoked as a Query, MUST return an array of Namespaces registered in the contextualized manufacturing information platform. All Namespaces MUST have a Namespace URI to support follow-up queries.

#### 3.3.2 Types

When invoked as a Query, MUST return an array of Type definitions registered in the contextualized manufacturing information platform. All Types MUST have an ElementId to support follow-up queries.

When invoked as a Query, if indicated by an optional query parameter, the response payload MAY by filtered by NamespaceURI.

#### 3.3.3 Type

When invoked as a Query, MUST return a JSON structure defining a Type registered in the contextualized manufacturing information platform for the requested Type's ElementId.

When invoked as a Query, MAY accept an array of JSON structures defining Types for the requested ElementIds to reduce round-trips where multiple Type definitions are required by an application, in which case, the return payload MUST be an array of arrays.

#### 3.4.3 ObjectsByType

When invoked as a Query, MUST return an array of instance objects that are of the requested Type's ElementId.

#### 3.4.4 ObjectByElementId

When invoked as a Query, if the ElementId exists as an instance object, MUST return the instance object, conforming to the Type definition the instance object derives from, and including the current value, if present, of any attribute.

When invoked as a Query, MAY accept an array of JSON structures defining Types for the requested ElementIds to reduce round-trips where multiple instance object definitions are required by an application, in which case, the return payload MUST be an array of arrays.

Recognizing that some systems allow some Type tolerance or looseness, when invoked as a Query, MAY accept a target Type, which would allow the CMIP to attempt Type casting or coercion on behalf of the invoking application.

#### 3.4.5 RelationshipTypes

##### 3.4.5.1 HierarchicalRelationshipTypes

When invoked as a Query, MUST return the relationship types HasChild, HasParent. MAY return additional hierarchical relationship types. These relationship type names SHALL be treated as keywords for follow-up queries. 

##### 3.4.5.2 NonHierarchicalRelationshipTypes

When invoked as a Query, MAY return any graph-style relationship types the contextualized manufacturing information platform supports, excluding the HierarchicalRelationshipTypes. These relationship type names SHALL be treated as keywords for follow-up queries.

##### 3.4.6 RelationshipsOfType

When invoked as a Query, MUST return an array of objects related to the requested ElementId by the Type name of relationship specified in the query.

When invoked as a Query, if specified by an optional query parameter, an implementation MAY support following relationships to the specified depth.

## 4. CMIP Requirements

To support the CMIAPI, a CMIP must have certain capabilities. While this, and subsequent, RFCs will not define requirements for implementation specifics, some base functionality must exist. Vendors MAY differentiate on optimization, performance and scalability, to meet the requirements of the API.

### 4.1 Object Orientation

The reader will observe that the API requires the underlying platform to support the idea of organizing data into objects with attributes. Those objects MUST be composable using other objects. Implementations MAY choose to have attributes of different flavors internally (for example: OPC UA differentiates between properties and variables), but MUST simplify those variations to object parameters to support easy-to-consume JSON serialization. If the calling application requests additional metadata for an object, an implementation MAY return details about its specific attribute behavior (as described in 3.1.1 and 3.1.2)

### 4.2 Type Safety

#### 4.2.1 Data Type Definitions

Underlying platforms MAY persist data values using any primitive types they wish, but MUST support return attribute values (both Live and Historical) cast or coerced to one of the primitive JavaScript primitive types to support JSON serialization (eg: a value persisted as FLOAT must be returned as NUMBER).

#### 4.2.2 Complex Type Definitions

Underlying platforms MUST derive Objects from separately declared definitions (also known as Class, Template or Schema definitions in other environments). In the CMIAPI, these definitions are generalized as Type definitions, given first-class treatment, and MUST be serializable to easy-to-consume JSON. Implementing platforms MUST support importing Type definitions from the [OPC UA Part 5 Information Modeling standard](https://reference.opcfoundation.org/Core/Part5/v104/docs/) (IEC62541-5). Implementing platforms MAY support importing Type definitions from the [Asset Administration Shell SubModelTemplate standard](https://www.zvei.org/fileadmin/user_upload/Presse_und_Medien/Publikationen/2020/Dezember/Submodel_Templates_of_the_Asset_Administration_Shell/201117_I40_ZVEI_SG2_Submodel_Spec_ZVEI_Technical_Data_Version_1_1.pdf). Implementing platforms MAY also support an internal Type definition and storage format.

### 4.3 Relationships

#### 4.3.1 Derivation

As described in 4.2.2, Objects are derived from Types. This derivation is a relationship that MUST be persisted by underlying platforms in order to support queries in the API.

#### 4.3.2 Hierarchical Relationships

To properly support Object Orientation, underlying platforms MUST support hierarchical relationships between Objects. These common relationships, such as parent-child, are table stakes for any contextualized manufacturing information platform.

#### 4.3.3 Non-Hierarchical Relationships

Modern contextualized manufacturing information platforms should be able to track relationships between objects that are not strictly hierarchical. Examples include "equipment train" relationships in ISA-95, supply chain relationships that track material flow, and human resource relationships where qualified operators can be associated with equipment they have been certified on. Modern information platforms SHOULD include support for non-hierarchical relationships.

### 4.4 Security Considerations

#### 4.4.1 Authorization

As a programmer's interface, this RFC primarily considers application authorization: implementations MUST support authorization using API keys as a minimum. Implementations MAY choose to replace API keys with JWT or OAuth. 

#### 4.4.2 Authentication

Implementations MAY require user authentication in order to refine application authorization for some or all of the data the API supports.

#### 4.4.3 Encryption

Implementations MUST require HTTPS for all communication. Implementations MUST NOT support un-encrypted HTTP in production.

### 4.5 Address Space

The complete collection of Relationship Types and Relationships, Object Types and Object Instances persisted in a contextualized manufacturing information platform SHALL be referred to as the Address Space. Implementations of this API MUST have the entire Address Space readily available for querying, this is an anti-pattern for implementations like a OPC UA server, where the Address Space "unfolds" through multiple Browse queries. 

### 4.6 Performance Considerations

While this API suggests that large volumes of Structural and Historical data will be accessible, the reality of many underlying data sources is that it may take multiple calls (for example, to browse an Address Space in the case of OPC/UA, or to fetch history from a separate store where a MQTT Broker is paired with a Historian) to respond to a given query. While it is the intent of this proposal to provide such abstraction -- shielding an application developer from the complexity of such architectures -- obvious performance implications exist. This proposal cannot prescribe how to solve all of these issues, but implementers MAY consider the following:

- Implementations MAY use an in-memory cache, on-disk database, or some hybrid for frequently accessed data, as long as Exploratory Interface queries can be responded to promptly.
- Implementations MAY pre-fetch data, such as pre-browsing an Address Space in a background thread.
- Implementations MAY require query limits or windows, to manage the size of requests or responses.
- Implementations MAY choose to persist state, using authentication, a session, or some token.

Implementations of this API MUST have Current Values for all persisted Object Instances, including their attribute values, readily available for querying. Implementations that are not connected directly to a manufacturing data source (eg: Cloud platforms, Historians) MUST return the most recent value received from the underlying data source.

Implementations of this API MUST be able to return Historical Value responses within a common HTTP client timeout (currently Firefox and Chrome use 300 seconds as a default.) If the complete payload cannot be returned within this time frame, a partial payload and poll-able callback URL MUST be returned.

## 5. Acknowledgements

Unless requested otherwise, contributor names and organizations from private previews of this document will be acknowledged in the public release.