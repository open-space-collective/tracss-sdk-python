# Reference
## BulkData Tip
<details><summary><code>client.bulk_data.tip.<a href="src/tracss/bulk_data/tip/client.py">stream</a>(...) -> typing.Iterator[bytes]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Find all TIP reports in the system or all reports that meet your search criteria defined by the query parameters.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.bulk_data.tip.stream(
    norad_id="noradId=12345",
    id="id=87",
    msg_epoch="msgEpoch=2004-09-28T02:49:00.000Z",
    insert_epoch="insertEpoch=2004-09-28T02:49:00.000Z",
    decay_epoch="decayEpoch=2004-09-28T02:49:00.000Z",
    window="window=900",
    rev="rev=25952",
    direction="direction=descending",
    latitude="latitude=36.0",
    longitude="longitude=217.5",
    inclination="inclination=53.0",
    next_report="decayEpoch=48",
    high_interest="highInterest=Y",
    format="json",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**norad_id:** `typing.Optional[str]` — The noradId of an object. Valid operators are: Equal (=Value), Not Equal (=<>Value), Greater Than or Equal (=>=Value), Greater Than (=>Value), Less Than or Equal (=<=Value), Less Than (=<Value), In (=Value1,Value2,etc), Between (=Value1...Value2)
    
</dd>
</dl>

<dl>
<dd>

**id:** `typing.Optional[str]` — The numeric id of the TIP report. Valid operators are: Equal (=Value), Not Equal (=<>Value), Greater Than or Equal (=>=Value), Greater Than (=>Value), Less Than or Equal (=<=Value), Less Than (=<Value), In (=Value1,Value2,etc), Between (=Value1...Value2)
    
</dd>
</dl>

<dl>
<dd>

**msg_epoch:** `typing.Optional[str]` — Timestamp of when of the TIP report was produced. Valid operators are: Equal (=Value), Not Equal (=<>Value), Greater Than or Equal (=>=Value), Greater Than (=>Value), Less Than or Equal (=<=Value), Less Than (=<Value), Between (=Value1...Value2)
    
</dd>
</dl>

<dl>
<dd>

**insert_epoch:** `typing.Optional[str]` — Timestamp of when the record was inserted in the system. Valid operators are: Equal (=Value), Not Equal (=<>Value), Greater Than or Equal (=>=Value), Greater Than (=>Value), Less Than or Equal (=<=Value), Less Than (=<Value), Between (=Value1...Value2)
    
</dd>
</dl>

<dl>
<dd>

**decay_epoch:** `typing.Optional[str]` — Timestamp of the predicted time of atmospheric re-entry. Valid operators are: Equal (=Value), Not Equal (=<>Value), Greater Than or Equal (=>=Value), Greater Than (=>Value), Less Than or Equal (=<=Value), Less Than (=<Value), Between (=Value1...Value2)
    
</dd>
</dl>

<dl>
<dd>

**window:** `typing.Optional[str]` — The uncertainty window around the re-entry time in seconds. Valid operators are: Equal (=Value), Not Equal (=<>Value), Greater Than or Equal (=>=Value), Greater Than (=>Value), Less Than or Equal (=<=Value), Less Than (=<Value), In (=Value1,Value2,etc), Between (=Value1...Value2)
    
</dd>
</dl>

<dl>
<dd>

**rev:** `typing.Optional[str]` — The orbit revolution number at the time of prediction. Valid operators are: Equal (=Value), Not Equal (=<>Value), Greater Than or Equal (=>=Value), Greater Than (=>Value), Less Than or Equal (=<=Value), Less Than (=<Value), In (=Value1,Value2,etc), Between (=Value1...Value2)
    
</dd>
</dl>

<dl>
<dd>

**direction:** `typing.Optional[str]` — The direction of orbital trajectory during re-entry prediction. Valid operators are: Equal (=Value), Not Equal (=<>Value), Like (=\*Value), Not Like (=~*Value). Possible values: ascending and descending.
    
</dd>
</dl>

<dl>
<dd>

**latitude:** `typing.Optional[str]` — The latitude of predicted re-entry location. Valid operators are: Equal (=Value), Not Equal (=<>Value), Greater Than or Equal (=>=Value), Greater Than (=>Value), Less Than or Equal (=<=Value), Less Than (=<Value), In (=Value1,Value2,etc), Between (=Value1...Value2)
    
</dd>
</dl>

<dl>
<dd>

**longitude:** `typing.Optional[str]` — Longitude of predicted re-entry location. Valid operators are: Equal (=Value), Not Equal (=<>Value), Greater Than or Equal (=>=Value), Greater Than (=>Value), Less Than or Equal (=<=Value), Less Than (=<Value), In (=Value1,Value2,etc), Between (=Value1...Value2)
    
</dd>
</dl>

<dl>
<dd>

**inclination:** `typing.Optional[str]` — Inclination of the orbit at time of prediction. Valid operators are: Equal (=Value), Not Equal (=<>Value), Greater Than or Equal (=>=Value), Greater Than (=>Value), Less Than or Equal (=<=Value), Less Than (=<Value), In (=Value1,Value2,etc), Between (=Value1...Value2)
    
</dd>
</dl>

<dl>
<dd>

**next_report:** `typing.Optional[str]` — Estimated time in hours until next update (Integer). Valid operators are: Equal (=Value), Not Equal (=<>Value), Greater Than or Equal (=>=Value), Greater Than (=>Value), Less Than or Equal (=<=Value), Less Than (=<Value), In (=Value1,Value2,etc), Between (=Value1...Value2)
    
</dd>
</dl>

<dl>
<dd>

**high_interest:** `typing.Optional[str]` — Flag indicating if object is considered high interest for re-entry tracking. Valid operators are: Equal (=Value), Not Equal (=<>Value), Like (=\*Value), Not Like (=~*Value). Possible values: Y, N
    
</dd>
</dl>

<dl>
<dd>

**format:** `typing.Optional[str]` — Format of the request body. KVN, JSON, and XML are all valid formats. JSON is default.
    
</dd>
</dl>

<dl>
<dd>

**size:** `typing.Optional[int]` — Number of TIP Reports to return.
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — Page number for the queried TIP(s), indexed by 0 (first page). Default is 0
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## BulkData Ocm
<details><summary><code>client.bulk_data.ocm.<a href="src/tracss/bulk_data/ocm/client.py">stream</a>(...) -> typing.Iterator[bytes]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve one or more TraCSS V2 OCMs from TRACSS cloud storage.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.bulk_data.ocm.stream(
    created_by="some_ephem.ocm",
    creation_date="2024-09-04T18:37:01Z",
    message_id="000043928_conj_000054603_2024329195621",
    operator="some_user",
    owner="some_user",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**constellation:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**created_by:** `typing.Optional[str]` — Filename of the file that created the OCM.A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2) , Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**creation_date:** `typing.Optional[str]` — Creation Date of the OCM. A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value) and Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**message_id:** `typing.Optional[str]` — Message Id of the OCM. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2) , Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object_designator:** `typing.Optional[str]` — The designator for OCM object.A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value), In (Value1,Value2), Between (Value1...Value2) (smaller value first), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**operator:** `typing.Optional[str]` — Name of operator.A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2) , Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**owner:** `typing.Optional[str]` — Name of the object owner.A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2) , Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**start_time:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**stop_time:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**traj_basis:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**max_creation_date:** `typing.Optional[str]` — Retrieve only the latest OCM per object designator.
    
</dd>
</dl>

<dl>
<dd>

**size:** `typing.Optional[int]` — Number of results to return.  Default of 0 means return all possible results.
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — Page number for the queried OCM(s), indexed by 0 (first page). Default is 0
    
</dd>
</dl>

<dl>
<dd>

**headers_only:** `typing.Optional[bool]` — Return a reduced object. works with filters messageId, creationDate, objectDesignator, operator
    
</dd>
</dl>

<dl>
<dd>

**format:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.bulk_data.ocm.<a href="src/tracss/bulk_data/ocm/client.py">stream_v1</a>(...) -> typing.Iterator[bytes]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve one or more TraCSS V1 OCMs from TRACSS cloud storage.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.bulk_data.ocm.stream_v1(
    created_by="some_ephem.ocm",
    creation_date="2024-09-04T18:37:01Z",
    message_id="000043928_conj_000054603_2024329195621",
    operator="some_user",
    owner="some_user",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**constellation:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**created_by:** `typing.Optional[str]` — Filename of the file that created the OCM.A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2) , Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**creation_date:** `typing.Optional[str]` — Creation Date of the OCM. A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value) and Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**message_id:** `typing.Optional[str]` — Message Id of the OCM. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2) , Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object_designator:** `typing.Optional[str]` — The designator for OCM object.A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value), In (Value1,Value2), Between (Value1...Value2) (smaller value first), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**operator:** `typing.Optional[str]` — Name of operator.A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2) , Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**owner:** `typing.Optional[str]` — Name of the object owner.A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2) , Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**start_time:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**stop_time:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**traj_basis:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**tech_org:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**tech_poc:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**size:** `typing.Optional[int]` — Number of results to return.  Default of 0 means return all possible results.
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — Page number for the queried OCM(s), indexed by 0 (first page). Default is 0
    
</dd>
</dl>

<dl>
<dd>

**headers_only:** `typing.Optional[bool]` — Return a reduced object. works with filters messageId, creationDate, objectDesignator, operator
    
</dd>
</dl>

<dl>
<dd>

**format:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## BulkData Cdm
<details><summary><code>client.bulk_data.cdm.<a href="src/tracss/bulk_data/cdm/client.py">stream</a>(...) -> typing.Iterator[bytes]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve one or more TraCSS V2 CDMs from TRACSS cloud storage.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.bulk_data.cdm.stream(
    message_id="000043928_conj_000054603_2024329195621",
    tca="2024-314T07:41:39.411",
    creation_date="2024-09-04T18:37:01Z",
    message_for="IRIDIUM 161",
    screening_option="Covariance",
    screen_volume_shape="Box, Ellipsoid, Deep Space",
    object1type="Payload",
    object1international_designator="2019-002A",
    object1operator_organization="Iridium",
    object1ephemeris_name="NONE",
    object2type="Payload",
    object2international_designator="2019-002A",
    object2operator_organization="Iridium",
    object2ephemeris_name="NONE",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**message_id:** `typing.Optional[str]` — Message Id (generated) from ASW that processed the CDM during super combo processing.A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**correlation_id:** `typing.Optional[str]` — Correlation Id (UUID) of the TraCSS CDM.A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**tca:** `typing.Optional[str]` — TCA (Time of Closest Approach).A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value),Less Than or Equal (<=Value), Not Equal (<>Value) and Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**creation_date:** `typing.Optional[str]` — Creation Date of the CDM.A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value),Less Than or Equal (<=Value), Not Equal (<>Value) and Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**message_for:** `typing.Optional[str]` — Name of Satellite whom the TraCSS cdm is for.A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**screening_option:** `typing.Optional[str]` — What was used during the screening process.A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**miss_distance:** `typing.Optional[str]` — The distance (in m) that object1 and object2 missed by. A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value), In (Value1,Value2) , Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**collision_probability:** `typing.Optional[str]` — The probability of object1 and object2 having a collision.A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value), In (Value1,Value2) , Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**screen_volume_shape:** `typing.Optional[str]` — The shape of the screen volume for object1A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1type:** `typing.Optional[str]` — The object type of object1A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1object_designator:** `typing.Optional[str]` — The designator for object1A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1international_designator:** `typing.Optional[str]` — The international designator for object1A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1operator_organization:** `typing.Optional[str]` — The operator organization for object1A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1ephemeris_name:** `typing.Optional[str]` — The ephemeris name for object1A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2type:** `typing.Optional[str]` — The object type of object2A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2object_designator:** `typing.Optional[str]` — The designator for object2A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2international_designator:** `typing.Optional[str]` — The international designator for object2A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2operator_organization:** `typing.Optional[str]` — The operator organization for object2A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2ephemeris_name:** `typing.Optional[str]` — The ephemeris name for object2A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**headers_only:** `typing.Optional[bool]` — Return a reduced object. The filters that work with headersOnly are: correlationId, creationDate, messageId, tca, missDistance, collisionProbability, object1ObjectDesignator, object2ObjectDesignator
    
</dd>
</dl>

<dl>
<dd>

**size:** `typing.Optional[int]` — Number of results to return.  Default of 0 means return all possible results.
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — Page number for the queried CDM(s), indexed by 0 (first page). Default is 0
    
</dd>
</dl>

<dl>
<dd>

**format:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.bulk_data.cdm.<a href="src/tracss/bulk_data/cdm/client.py">stream_v1</a>(...) -> typing.Iterator[bytes]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve one or more TraCSS V1 CDMs from TRACSS cloud storage.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.bulk_data.cdm.stream_v1(
    message_id="000043928_conj_000054603_2024329195621",
    tca="2024-314T07:41:39.411",
    creation_date="2024-09-04T18:37:01Z",
    message_for="IRIDIUM 161",
    screening_option="Covariance",
    object1screen_volume_shape="Box, Ellipsoid, Deep Space",
    object1type="Payload",
    object1international_designator="2019-002A",
    object1operator_organization="Iridium",
    object1ephemeris_name="NONE",
    object2screen_volume_shape="Box, Ellipsoid, Deep Space",
    object2type="Payload",
    object2international_designator="2019-002A",
    object2operator_organization="Iridium",
    object2ephemeris_name="NONE",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**message_id:** `typing.Optional[str]` — Message Id (generated) from ASW that processed the CDM during super combo processing.A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**correlation_id:** `typing.Optional[str]` — Correlation Id (UUID) of the TraCSS CDM.A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**tca:** `typing.Optional[str]` — TCA (Time of Closest Approach).A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value),Less Than or Equal (<=Value), Not Equal (<>Value) and Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**creation_date:** `typing.Optional[str]` — Creation Date of the CDM.A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value),Less Than or Equal (<=Value), Not Equal (<>Value) and Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**message_for:** `typing.Optional[str]` — Name of Satellite whom the TraCSS cdm is for.A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**screening_option:** `typing.Optional[str]` — What was used during the screening process.A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**miss_distance:** `typing.Optional[str]` — The distance (in m) that object1 and object2 missed by. A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value), In (Value1,Value2) , Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**collision_probability:** `typing.Optional[str]` — The probability of object1 and object2 having a collision.A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value), In (Value1,Value2) , Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**object1screen_volume_shape:** `typing.Optional[str]` — The shape of the screen volume for object1A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1type:** `typing.Optional[str]` — The object type of object1A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1object_designator:** `typing.Optional[str]` — The designator for object1A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1international_designator:** `typing.Optional[str]` — The international designator for object1A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1operator_organization:** `typing.Optional[str]` — The operator organization for object1A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1ephemeris_name:** `typing.Optional[str]` — The ephemeris name for object1A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2screen_volume_shape:** `typing.Optional[str]` — The shape of the screen volume for object2A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2type:** `typing.Optional[str]` — The object type of object2A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2object_designator:** `typing.Optional[str]` — The designator for object2A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2international_designator:** `typing.Optional[str]` — The international designator for object2A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2operator_organization:** `typing.Optional[str]` — The operator organization for object2A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2ephemeris_name:** `typing.Optional[str]` — The ephemeris name for object2A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**size:** `typing.Optional[int]` — Number of results to return.  Default of 0 means return all possible results.
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — Page number for the queried CDM(s), indexed by 0 (first page). Default is 0
    
</dd>
</dl>

<dl>
<dd>

**format:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## BulkData Announcements
<details><summary><code>client.bulk_data.announcements.<a href="src/tracss/bulk_data/announcements/client.py">list</a>(...) -> str</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Fetches a list of announcements data from cloud storage.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.bulk_data.announcements.list(
    type="EMERGENCY",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**type:** `typing.Optional[str]` — Type/Criticality of Announcement.  Can be INFORMATION, OUTAGE, or EMERGENCY.
    
</dd>
</dl>

<dl>
<dd>

**size:** `typing.Optional[int]` — Number of results returned. A default of 0 will return all possible results.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Metadata ContactDirectory
<details><summary><code>client.metadata.contact_directory.<a href="src/tracss/metadata/contact_directory/client.py">update_operational</a>(...) -> Operator</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Updates an existing Satellite Operator record in the database based on the provided noradId(s) and data in the request body. Returns the updated Operator object as JSON.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.metadata.contact_directory.update_operational(
    norad_ids=[
        "noradIds"
    ],
    request={
        "operatorPoc": "string",
        "operatorPhone": "string",
        "operatorEmail": "string"
    },
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request:** `typing.Dict[str, typing.Any]` 
    
</dd>
</dl>

<dl>
<dd>

**norad_ids:** `typing.Optional[typing.Union[str, typing.Sequence[str]]]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.metadata.contact_directory.<a href="src/tracss/metadata/contact_directory/client.py">list_operational</a>(...) -> typing.List[OperationalContactInfoDto]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

This endpoint allows TraCSS users to retrieve operational contact information for all registered satellites in TraCSS. This includes the name, email, and phone numbers for all POCs of a satellite group
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.metadata.contact_directory.list_operational(
    organization="SpaceX",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**norad_id:** `typing.Optional[str]` — Specific Norad ID or Norad IDs to find contact info for. See OperatorContactInfoByNoradIdDTO Schema for response format.
    
</dd>
</dl>

<dl>
<dd>

**organization:** `typing.Optional[str]` — Specific organization or organizations to find contact information for. See default schema for response format.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Metadata Ocm
<details><summary><code>client.metadata.ocm.<a href="src/tracss/metadata/ocm/client.py">upload</a>(...) -> typing.Dict[str, typing.Any]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Upload a V2 OCM or zip file of OCMs (file param in formData). If you wish to update the database, use a header of updateDatabase with a value of true.The following will be used from the OCM:
* Tech POC
* Tech Org
* Tech Position
* Tech Phone
* Tech Email
* Tech Address
* Originator POC
* Originator Position
* Originator Phone
* Originator Email
* Originator Address
* Ops Status
* Orbit Category
* Wet mass
* Hard Body Radius
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.metadata.ocm.upload(
    file="example_file",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**file:** `core.File` 
    
</dd>
</dl>

<dl>
<dd>

**trigger_ca:** `typing.Optional[bool]` — Whether to trigger CA with uploaded OCM(s). Defaults to false. NOTE: This only affects OPERATIONAL OCMs, CANDIDATE OCMs will always trigger on-demand CA NOTE: If two Operational OCMs with the same objectId are uploaded, only the most recently created OCM will be screened for on demand.
    
</dd>
</dl>

<dl>
<dd>

**update_database:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.metadata.ocm.<a href="src/tracss/metadata/ocm/client.py">upload_v1</a>(...) -> typing.Dict[str, typing.Any]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Upload an OCM or zip file of OCMs (file param in formData). If you wish to update the database, use a header of updateDatabase with a value of true.The following will be used from the OCM:
* Tech POC
* Tech Org
* Tech Position
* Tech Phone
* Tech Email
* Tech Address
* Originator POC
* Originator Position
* Originator Phone
* Originator Email
* Originator Address
* Ops Status
* Orbit Category
* Wet mass
* Hard Body Radius
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.metadata.ocm.upload_v1(
    file="example_file",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**file:** `core.File` 
    
</dd>
</dl>

<dl>
<dd>

**trigger_ca:** `typing.Optional[bool]` — Whether to trigger CA with uploaded OCM(s). Defaults to false. NOTE: This only affects OPERATIONAL OCMs, CANDIDATE OCMs will always trigger on-demand CA NOTE: If two Operational OCMs with the same objectId are uploaded, only the most recently created OCM will be screened for on demand.
    
</dd>
</dl>

<dl>
<dd>

**update_database:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.metadata.ocm.<a href="src/tracss/metadata/ocm/client.py">list</a>(...) -> ListOcmResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve one or more OCMs from TRACSS. If no parameters are provided, the system will default to the header of all OCMs currently stored.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.metadata.ocm.list(
    owner="ABCCorporation",
    operator="CDECorporation",
    message_id="d4c8f1b1-2652-4b33-b78b-9e5f0429ff08",
    file_name="d4c8f1b1-2652-4b33-b78b-9e5f0429ff08",
    creation_date="2024-09-04T18:37:01Z",
    format="json",
    sort="objectDesignator,ASC",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**owner:** `typing.Optional[str]` — Owner of the satellite. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2) , Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**operator:** `typing.Optional[str]` — Operator of the satellite. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2) , Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object_designator:** `typing.Optional[str]` — Object Designator (Satellite Number). A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value), In (Value1,Value2), Between (Value1...Value2) (smaller value first), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**message_id:** `typing.Optional[str]` — Message Id (UUID) of the OCM. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**file_name:** `typing.Optional[str]` — File name of the OCM. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**creation_date:** `typing.Optional[str]` — Creation Date of the OCM. A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value), and Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**headers_only:** `typing.Optional[bool]` — Only get the header key fields of the object being asked for. Default is false. If set to true, format will be overwritten to JSON. Does not work with any filters
    
</dd>
</dl>

<dl>
<dd>

**max_creation_date:** `typing.Optional[bool]` — Retrieve only the latest OCM per object designator.
    
</dd>
</dl>

<dl>
<dd>

**format:** `typing.Optional[str]` — Desired format of the returned OCM(s). Options are KVN (Default), JSON or XML.
    
</dd>
</dl>

<dl>
<dd>

**sort:** `typing.Optional[str]` — Desired sort field and direction (ASC, DESC).
    
</dd>
</dl>

<dl>
<dd>

**fields:** `typing.Optional[str]` 

Comma separated list of specific fields to include in the response.  Valid fields for JSON and XML are: OEB_MIN, WET_MASS, VM_ABSOLUTE, MAN_PREV_ID, ADM_MSG_LINK, ACTUAL_OD_SPAN, OWNER, TRAJ_BASIS_ID, TRAJ_ID, MAN_BASIS, MAN_FRAME_EPOCH, COV_CONFIDENCE, VM_APPARENT_MAX, DC_TYPE, MAXIMUM_OBS_GAP, CONSTELLATION, OD_EPOCH_EIGMIN, MAN_VALUES, START_TIME, RCS, SEDR, SW_DATA_EPOCH, GRAVITY_MODEL, EQUATORIAL_RADIUS, TDM_MSG_LINK, MESSAGE_ID, CELESTIAL_SOURCE, OD_EPOCH_EIGINT, PREVIOUS_MESSAGE_ID, MAN_NEXT_ID, DRAG_COEFF_NOM
, COV_BASIS_ID, CATALOG_NAME, RCS_MIN, UT1MUTC_AT_TZERO, MAN_PREV_EPOCH, OEB_PARENT_FRAME, PREVIOUS_MESSAGE_EPOCH, MAX_THRUST, TECH_ADDRESS, COV_VALUES, RDM_MSG_LINK, OPERATOR, ATT_KNOWLEDGE, COV_SCALE_MAX, DC_BODY_TRIGGER, ORB_REVNUM, INTERPOLATION_DEGREE, OBJECT_NAME, MAN_PURPOSE, DV_BOL, AREA_ALONG_OEB_MIN, VM_APPARENT, SHADOW_BODIES, FIXED_GEOMAG_DST, INTERPOLATION, DC_MIN_CYCLES, COV_BASIS, TECH_POC, COUNTRY, 
COV_UNITS, ATT_ACTUATOR_TYPE, MAN_REF_FRAME, INTERNATIONAL_DESIGNATOR, OEB_INT, FIXED_Y10P7_MEAN, ORIGINATOR_ADDRESS, COV_FRAME_EPOCH, ALBEDO_MODEL, DC_REF_TIME, hbr, SRP_CONST_AREA, OEB_QC, SOLID_TIDES_MODEL, COV_ID, NEXT_MESSAGE_ID, CENTRAL_BODY_ROTATION, OD_EPOCH, REFLECTANCE, MAN_DEVICE_ID, MAN_BASIS_ID, DC_EXEC_STOP, ORBIT_CATEGORY, ALTERNATE_NAMES, BUS_MODEL, GM, COV_NEXT_ID, AREA_ALONG_OEB_INT, ATT_CONTROL_M
ODE, EPOCH_TZERO, SCLK_OFFSET_AT_EPOCH, INITIAL_WET_MASS, FIXED_S10P7, ORIGINATOR_PHONE, OBLATE_FLATTENING, FIXED_GEOMAG_AP, SW_DATA_SOURCE, OD_PREV_ID, FIXED_F10P7, IXX, REDUCTION_THEORY, IXZ, IXY, DC_WIN_CLOSE, SENSORS, VM_APPARENT_MIN, ORIGINATOR_POSITION, DAYS_SINCE_FIRST_OBS, DOCKED_WITH, RCS_MAX, NEXT_MESSAGE_EPOCH, DAYS_SINCE_LAST_OBS, OEB_PARENT_FRAME_EPOCH, DC_BODY_FRAME, AREA_TYP_FOR_PC, FIXED_M10P7, OCEA
N_TIDES_MODEL, OD_EPOCH_EIGMAJ, OEB_MAX, IYY, WEIGHTED_RMS, CLASSIFICATION, IYZ, OCM_DATA_ELEMENTS, USEABLE_START_TIME, COV_REF_FRAME, RECOMMENDED_OD_SPAN, OD_MAX_PRED_EIGMAJ, COV_PREV_ID, TRACKS_AVAILABLE, OD_METHOD, CONSIDER_N, SENSORS_N, ATT_POINTING, IZZ, OEB_Q1, CDM_MSG_LINK, ATMOSPHERIC_MODEL, AREA_MIN_FOR_PC, TRACKS_USED, DC_TIME_PULSE_DURATION, USER_DEFINED_HBR, OEB_Q2, EOP_SOURCE, OEB_Q3, COV_ORDERING, TRA
J_FRAME_EPOCH, SOLVE_STATES, DV_REMAINING, MAN_ID, SW_INTERP_METHOD, GDOP, TAIMUTC_AT_TZERO, OBS_USED, ORIGINATOR_POC, ORIGINATOR_EMAIL, COV_SCALE_MIN, ORB_REVNUM_BASIS, DC_PA_STOP_ANGLE, PRM_MSG_LINK, MANUFACTURER, INTERP_METHOD_EOP, TIME_SPAN, MAN_COMPOSITION, TIME_SYSTEM, TECH_PHONE, FIXED_Y10P7, CENTER_NAME, ALBEDO_GRID_SIZE, TRAJ_REF_FRAME, MAN_NEXT_EPOCH, MAN_PRED_SOURCE, DC_EXEC_START, CONSIDER_PARAMS, FIXED
_M10P7_MEAN, TRAJ_UNITS, DATA_TYPES, AREA_ALONG_OEB_MAX, TRAJ_BASIS, SOLAR_RAD_UNCERTAINTY, DC_REF_DIR, TRAJ_NEXT_ID, CREATION_DATE, DC_WIN_OPEN, FIXED_S10P7_MEAN, AVG_MANEUVER_FREQ, DC_PA_START_ANGLE, TECH_POSITION, N_BODY_PERTURBATIONS, SOLAR_RAD_COEFF, ORB_AVERAGING, DC_MAX_CYCLES, OD_ID, FIXED_F10P7_MEAN, DC_TIME_PULSE_PERIOD, OBJECT_DESIGNATOR, TRAJ_VALUES, FIXED_GEOMAG_KP, OBJECT_TYPE, ATT_CONTROL, TRAJ_PREV_
ID, DRAG_UNCERTAINTY, TECH_EMAIL, AREA_MAX_FOR_PC, SRP_MODEL, MAN_UNITS, ORIGINATOR, GRAV_ASSIST_NAME, SHADOW_MODEL, NEXT_LEAP_EPOCH, PROPAGATOR, TRAJ_TYPE, OD_CONFIDENCE, OPS_STATUS, DRY_MASS, SOLVE_N, SCLK_SEC_PER_SI_SEC, STOP_TIME, COV_TYPE, TECH_ORG, NEXT_LEAP_TAIMUTC, DRAG_CONST_AREA, OBS_AVAILABLE, USEABLE_STOP_TIME, OD_MIN_PRED_EIGMIN, OEB_MIN, WET_MASS, VM_ABSOLUTE, MAN_PREV_ID, ADM_MSG_LINK, ACTUAL_OD_SPAN
, OWNER, TRAJ_BASIS_ID, TRAJ_ID, MAN_BASIS, MAN_FRAME_EPOCH, COV_CONFIDENCE, VM_APPARENT_MAX, DC_TYPE, MAXIMUM_OBS_GAP, CONSTELLATION, OD_EPOCH_EIGMIN, MAN_VALUES, START_TIME, RCS, SEDR, SW_DATA_EPOCH, GRAVITY_MODEL, EQUATORIAL_RADIUS, TDM_MSG_LINK, MESSAGE_ID, CELESTIAL_SOURCE, OD_EPOCH_EIGINT, PREVIOUS_MESSAGE_ID, MAN_NEXT_ID, DRAG_COEFF_NOM, COV_BASIS_ID, CATALOG_NAME, RCS_MIN, UT1MUTC_AT_TZERO, MAN_PREV_EPOCH, 
OEB_PARENT_FRAME, PREVIOUS_MESSAGE_EPOCH, MAX_THRUST, TECH_ADDRESS, COV_VALUES, RDM_MSG_LINK, OPERATOR, ATT_KNOWLEDGE, COV_SCALE_MAX, DC_BODY_TRIGGER, ORB_REVNUM, INTERPOLATION_DEGREE, OBJECT_NAME, MAN_PURPOSE, DV_BOL, AREA_ALONG_OEB_MIN, VM_APPARENT, SHADOW_BODIES, FIXED_GEOMAG_DST, INTERPOLATION, DC_MIN_CYCLES, COV_BASIS, TECH_POC, COUNTRY, COV_UNITS, ATT_ACTUATOR_TYPE, MAN_REF_FRAME, INTERNATIONAL_DESIGNATOR, OE
B_INT, FIXED_Y10P7_MEAN, ORIGINATOR_ADDRESS, COV_FRAME_EPOCH, ALBEDO_MODEL, DC_REF_TIME, hbr, SRP_CONST_AREA, OEB_QC, SOLID_TIDES_MODEL, COV_ID, NEXT_MESSAGE_ID, CENTRAL_BODY_ROTATION, OD_EPOCH, REFLECTANCE, MAN_DEVICE_ID, MAN_BASIS_ID, DC_EXEC_STOP, ORBIT_CATEGORY, ALTERNATE_NAMES, BUS_MODEL, GM, COV_NEXT_ID, AREA_ALONG_OEB_INT, ATT_CONTROL_MODE, EPOCH_TZERO, SCLK_OFFSET_AT_EPOCH, INITIAL_WET_MASS, FIXED_S10P7, OR
IGINATOR_PHONE, OBLATE_FLATTENING, FIXED_GEOMAG_AP, SW_DATA_SOURCE, OD_PREV_ID, FIXED_F10P7, IXX, REDUCTION_THEORY, IXZ, IXY, DC_WIN_CLOSE, SENSORS, VM_APPARENT_MIN, ORIGINATOR_POSITION, DAYS_SINCE_FIRST_OBS, DOCKED_WITH, RCS_MAX, NEXT_MESSAGE_EPOCH, DAYS_SINCE_LAST_OBS, OEB_PARENT_FRAME_EPOCH, DC_BODY_FRAME, AREA_TYP_FOR_PC, FIXED_M10P7, OCEAN_TIDES_MODEL, OD_EPOCH_EIGMAJ, OEB_MAX, IYY, WEIGHTED_RMS, CLASSIFICATIO
N, IYZ, OCM_DATA_ELEMENTS, USEABLE_START_TIME, COV_REF_FRAME, RECOMMENDED_OD_SPAN, OD_MAX_PRED_EIGMAJ, COV_PREV_ID, TRACKS_AVAILABLE, OD_METHOD, CONSIDER_N, SENSORS_N, ATT_POINTING, IZZ, OEB_Q1, CDM_MSG_LINK, ATMOSPHERIC_MODEL, AREA_MIN_FOR_PC, TRACKS_USED, DC_TIME_PULSE_DURATION, USER_DEFINED_HBR, OEB_Q2, EOP_SOURCE, OEB_Q3, COV_ORDERING, TRAJ_FRAME_EPOCH, SOLVE_STATES, DV_REMAINING, MAN_ID, SW_INTERP_METHOD, GDOP
, TAIMUTC_AT_TZERO, OBS_USED, ORIGINATOR_POC, ORIGINATOR_EMAIL, COV_SCALE_MIN, ORB_REVNUM_BASIS, DC_PA_STOP_ANGLE, PRM_MSG_LINK, MANUFACTURER, INTERP_METHOD_EOP, TIME_SPAN, MAN_COMPOSITION, TIME_SYSTEM, TECH_PHONE, FIXED_Y10P7, CENTER_NAME, ALBEDO_GRID_SIZE, TRAJ_REF_FRAME, MAN_NEXT_EPOCH, MAN_PRED_SOURCE, DC_EXEC_START, CONSIDER_PARAMS, FIXED_M10P7_MEAN, TRAJ_UNITS, DATA_TYPES, AREA_ALONG_OEB_MAX, TRAJ_BASIS, SOLA
R_RAD_UNCERTAINTY, DC_REF_DIR, TRAJ_NEXT_ID, CREATION_DATE, DC_WIN_OPEN, FIXED_S10P7_MEAN, AVG_MANEUVER_FREQ, DC_PA_START_ANGLE, TECH_POSITION, N_BODY_PERTURBATIONS, SOLAR_RAD_COEFF, ORB_AVERAGING, DC_MAX_CYCLES, OD_ID, FIXED_F10P7_MEAN, DC_TIME_PULSE_PERIOD, OBJECT_DESIGNATOR, TRAJ_VALUES, FIXED_GEOMAG_KP, OBJECT_TYPE, ATT_CONTROL, TRAJ_PREV_ID, DRAG_UNCERTAINTY, TECH_EMAIL, AREA_MAX_FOR_PC, SRP_MODEL, MAN_UNITS, ORIGINATOR, GRAV_ASSIST_NAME, SHADOW_MODEL, NEXT_LEAP_EPOCH, PROPAGATOR, TRAJ_TYPE, OD_CONFIDENCE, OPS_STATUS, DRY_MASS, SOLVE_N, SCLK_SEC_PER_SI_SEC, STOP_TIME, COV_TYPE, TECH_ORG, NEXT_LEAP_TAIMUTC, DRAG_CONST_AREA, OBS_AVAILABLE, USEABLE_STOP_TIME, OD_MIN_PRED_EIGMIN,
oebMin, wetMass, vmAbsolute, manPrevId, admMsgLink, actualOdSpan, owner, trajBasisId, trajId, manBasis, manFrameEpoch, covConfidence, vmApparentMax, dcType, maxObsGap, constellation, odEpochElGMIN, manValues, startTime, rcs, sedr, swDataEpoch, gravityModel, equatorialRadius, tdmMsgLink, messageId, celestialSource, odEpochElGINT, prevMessageId, manNextId, dragCoeff, covBasisId, catalogName, rcsMin, ut1MUtcAtT0, manP
revEpoch, oebParentFrame, previousMessageEpoch, maxThrust, techAddress, covValues, rdmMsgLink, operator, attKnowledge, covScaleMax, dcBodyTrigger, orbRevnum, interpolationDegree, objectName, manPurpose, dvBol, areaAlongOebMin, vmApparent, shadowBodies, fixedGeomagDst, interpolation, dcMinCycles, covBasis, techPoc, country, covUnits, attActuatorType, manRefFrame, internationalDesignator, oebInt, fixedY10P7Mean, orig
inatorAddress, covFrameEpoch, albedoModel, dcRefTime, hbr, srpConstArea, oebQC, solidTidesModel, covId, nextMessageId, centralBodyRotation, odEpoch, reflectance, manDeviceId, manBasisId, dcExecStop, orbitCategory, alternateNames, busModel, gm, covNextId, areaAlongOebInt, attControlMode, epochT0, sclkOffsetAtEpoch, initialWetMass, fixedS10P7, originatorPhone, oblateFlattening, fixedGeomagAp, swDataSource, odPrevId, 
fixedF10P7, iXX, reductionTheory, iXZ, iXY, dcWinClose, sensors, vmApparentMin, originatorPosition, daysSinceFirstObs, dockedWith, rcsMax, nextMessageEpoch, daysSinceLastObs, oebParentFrameEpoch, dcBodyFrame, areaTypForPc, fixedM10P7, oceanTidesModel, odEpochElGMAJ, oebMax, iYY, weightedRms, classification, iYZ, ocmDataElements, useableStartTime, covRefFrame, recommendedOdSpan, odMaxPredEigMAJ, covPrevId, tracksAva
ilable, odMethod, considerN, sensorsN, attPointing, iZZ, oebQ1, cdmMsgLink, atmosphericModel, areaMinForPc, tracksUsed, dcTimePulseDuration, hbr, oebQ2, eopSource, oebQ3, covOrdering, trajFrameEpoch, solveStates, dvRemaining, manId, swInterpMethod, gdop, taimUtcAtT0, obsUsed, originatorPoc, originatorEmail, covScaleMin, orbRevnumBasis, dcPaStopAngle, prmMsgLink, manufacturer, interpMethodEop, timeSpan, manCompositi
on, timeSystem, techPhone, fixedY10P7, centerName, albedoGridSize, trajRefFrame, manNextEpoch, manPredSource, dcExecStart, considerParams, fixedM10P7Mean, trajUnits, dataTypes, areaAlongOebMax, trajBasis, solarRadUncertainty, dcRefDir, trajNextId, creationDate, dcWinOpen, fixedS10P7Mean, avgManeuverFreq, dcPaStartAngle, techPosition, nBodyPertubations, solarRadCoeff, orbAveraging, dcMaxCycles, odId, fixedF10P7Mean,
 dcTimePulsePeriod, objectDesignator, trajValues, fixedGeomagKp, objectType, attControl, trajPrevId, dragUncertainty, techEmail, areaMaxForPc, srpModel, manUnits, originator, gravAssistName, shadowModel, nextLeapEpoch, propagator, trajType, odConfidence, opsStatus, dryMass, solveN, sclkSecPerSiSec, stopTime, covType, techOrg, nextLeapTaimUtc, dragConstArea, obsAvailable, useableStopTime, odMaxPredEigMIN, oebMin, we
tMass, vmAbsolute, manPrevId, admMsgLink, actualOdSpan, owner, trajBasisId, trajId, manBasis, manFrameEpoch, covConfidence, vmApparentMax, dcType, maxObsGap, constellation, odEpochElGMIN, manValues, startTime, rcs, sedr, swDataEpoch, gravityModel, equatorialRadius, tdmMsgLink, messageId, celestialSource, odEpochElGINT, prevMessageId, manNextId, dragCoeff, covBasisId, catalogName, rcsMin, ut1MUtcAtT0, manPrevEpoch, 
oebParentFrame, previousMessageEpoch, maxThrust, techAddress, covValues, rdmMsgLink, operator, attKnowledge, covScaleMax, dcBodyTrigger, orbRevnum, interpolationDegree, objectName, manPurpose, dvBol, areaAlongOebMin, vmApparent, shadowBodies, fixedGeomagDst, interpolation, dcMinCycles, covBasis, techPoc, country, covUnits, attActuatorType, manRefFrame, internationalDesignator, oebInt, fixedY10P7Mean, originatorAddr
ess, covFrameEpoch, albedoModel, dcRefTime, hbr, srpConstArea, oebQC, solidTidesModel, covId, nextMessageId, centralBodyRotation, odEpoch, reflectance, manDeviceId, manBasisId, dcExecStop, orbitCategory, alternateNames, busModel, gm, covNextId, areaAlongOebInt, attControlMode, epochT0, sclkOffsetAtEpoch, initialWetMass, fixedS10P7, originatorPhone, oblateFlattening, fixedGeomagAp, swDataSource, odPrevId, fixedF10P7
, iXX, reductionTheory, iXZ, iXY, dcWinClose, sensors, vmApparentMin, originatorPosition, daysSinceFirstObs, dockedWith, rcsMax, nextMessageEpoch, daysSinceLastObs, oebParentFrameEpoch, dcBodyFrame, areaTypForPc, fixedM10P7, oceanTidesModel, odEpochElGMAJ, oebMax, iYY, weightedRms, classification, iYZ, ocmDataElements, useableStartTime, covRefFrame, recommendedOdSpan, odMaxPredEigMAJ, covPrevId, tracksAvailable, od
Method, considerN, sensorsN, attPointing, iZZ, oebQ1, cdmMsgLink, atmosphericModel, areaMinForPc, tracksUsed, dcTimePulseDuration, hbr, oebQ2, eopSource, oebQ3, covOrdering, trajFrameEpoch, solveStates, dvRemaining, manId, swInterpMethod, gdop, taimUtcAtT0, obsUsed, originatorPoc, originatorEmail, covScaleMin, orbRevnumBasis, dcPaStopAngle, prmMsgLink, manufacturer, interpMethodEop, timeSpan, manComposition, timeSy
stem, techPhone, fixedY10P7, centerName, albedoGridSize, trajRefFrame, manNextEpoch, manPredSource, dcExecStart, considerParams, fixedM10P7Mean, trajUnits, dataTypes, areaAlongOebMax, trajBasis, solarRadUncertainty, dcRefDir, trajNextId, creationDate, dcWinOpen, fixedS10P7Mean, avgManeuverFreq, dcPaStartAngle, techPosition, nBodyPertubations, solarRadCoeff, orbAveraging, dcMaxCycles, odId, fixedF10P7Mean, dcTimePulsePeriod, objectDesignator, trajValues, fixedGeomagKp, objectType, attControl, trajPrevId, dragUncertainty, techEmail, areaMaxForPc, srpModel, manUnits, originator, gravAssistName, shadowModel, nextLeapEpoch, propagator, trajType, odConfidence, opsStatus, dryMass, solveN, sclkSecPerSiSec, stopTime, covType, techOrg, nextLeapTaimUtc, dragConstArea, obsAvailable, useableStopTime, odMaxPredEigMIN
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — Page number for the queried OCM(s). Default is 0
    
</dd>
</dl>

<dl>
<dd>

**size:** `typing.Optional[int]` — Number of OCM(s) per page.  Max is 10
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.metadata.ocm.<a href="src/tracss/metadata/ocm/client.py">list_by_operational_batch</a>(...) -> typing.List[OperationalOnDemandBatchDto]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve one or more On Demand Batches.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.metadata.ocm.list_by_operational_batch(
    message_id="000043928_conj_000054603_2024329195621",
    batch_id="opebe5bc-95e9-4b11-9594-5d0c61e0b241",
    upload_date=">2024-09-04T18:37:01Z",
    usable_start_time=">2024-09-04T18:37:01Z",
    usable_stop_time=">2024-09-04T18:37:01Z",
    creation_date=">2024-09-04T18:37:01Z",
    created_by="all",
    sort="satNo,ASC",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**message_id:** `typing.Optional[str]` — Message Id (generated) from ASW that processed the CDM during super combo processing. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**batch_id:** `typing.Optional[str]` — Batch Id from the batch of OCMs that was uploaded. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**sat_no:** `typing.Optional[str]` — SatNo from the OCM that was uploaded as part of the batch. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**upload_date:** `typing.Optional[str]` — Upload Date from the OCM batch that was uploaded. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), and Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**usable_start_time:** `typing.Optional[str]` — usableStartTime from an OCM that was uploaded as part of the batch. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), and Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**usable_stop_time:** `typing.Optional[str]` — usableStopTime from an OCM that was uploaded as part of the batch. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), and Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**creation_date:** `typing.Optional[str]` — creationDate from an OCM that was uploaded as part of the batch. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), and Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**cdm_found:** `typing.Optional[str]` — If a cdm is found as part of the batch on-demand run. Valid operators are: Not Equal (<>Value)
    
</dd>
</dl>

<dl>
<dd>

**created_by:** `typing.Optional[str]` — Username of batches to find. Can be a specific username or 'all' for all users. Defaults to requesting user's username
    
</dd>
</dl>

<dl>
<dd>

**sort:** `typing.Optional[str]` — Desired sort field and direction (Ascending = ASC, Descending = DESC), separated by a comma.
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — Page number for the queried TraCSS CDM(s). Default is 0
    
</dd>
</dl>

<dl>
<dd>

**size:** `typing.Optional[int]` — Number of TraCSS CDMs per page.  Max is 100000
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.metadata.ocm.<a href="src/tracss/metadata/ocm/client.py">list_v1</a>(...) -> ListV1OcmResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve one or more OCMs from TRACSS. If no parameters are provided, the system will default to the header of all OCMs currently stored.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.metadata.ocm.list_v1(
    owner="ABCCorporation",
    operator="CDECorporation",
    message_id="d4c8f1b1-2652-4b33-b78b-9e5f0429ff08",
    file_name="d4c8f1b1-2652-4b33-b78b-9e5f0429ff08",
    creation_date="2024-09-04T18:37:01Z",
    format="json",
    sort="objectDesignator,ASC",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**owner:** `typing.Optional[str]` — Owner of the satellite. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2) , Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**operator:** `typing.Optional[str]` — Operator of the satellite. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2) , Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object_designator:** `typing.Optional[str]` — Object Designator (Satellite Number). A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value), In (Value1,Value2), Between (Value1...Value2) (smaller value first), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**message_id:** `typing.Optional[str]` — Message Id (UUID) of the OCM. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**file_name:** `typing.Optional[str]` — File name of the OCM. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value) and Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**creation_date:** `typing.Optional[str]` — Creation Date of the OCM. A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value)
    
</dd>
</dl>

<dl>
<dd>

**headers_only:** `typing.Optional[bool]` — Only get the header key fields of the object being asked for. Default is false. If set to true, format will be overwritten to JSON. Does not work with any filters
    
</dd>
</dl>

<dl>
<dd>

**max_creation_date:** `typing.Optional[bool]` — Retrieve only the latest OCM per object designator.
    
</dd>
</dl>

<dl>
<dd>

**format:** `typing.Optional[str]` — Desired format of the returned OCM(s). Options are KVN (Default), JSON or XML.
    
</dd>
</dl>

<dl>
<dd>

**sort:** `typing.Optional[str]` — Desired sort field and direction (ASC, DESC).
    
</dd>
</dl>

<dl>
<dd>

**fields:** `typing.Optional[str]` 

Comma separated list of specific fields to include in the response.  Valid fields for JSON and XML are: cdmMsgLink, oebQ3, oebQ2, oebQ1, oebParentFrameEpoch, internationalDesignator, nextMessageEpoch, constellation, oebQC, gravAssistName, orbitCategory, dcPaStopAngle, covUnits, techOrg, fixedGeomagKp, shadowModel, oebInt, celestialSource, manNextId, dcRefTime, nextLeapEpoch, swDataSource, trajBasisId, originatorPhone, manId, dragUncertainty, covOrdering, oebMin, originatorAddress, dcMinCycles, tracksUsed, covBasisId,
 oblateFlattening, sensorsN, fixedM10P7Mean, dcBodyTrigger, solarRadCoeff, sedr, dcPaStartAngle, taimUtcAtT0, trajBasis, rcs, vmApparentMin, manBasisId, dcType, avgManeuverFreq, orbRevNum, manPurpose, ut1MUtcAtT0, solidTidesModel, tdmMsgLink, swInterpMethod, alternateNames, fixedY10P7, manNextEpoch, dryMass, dvBol, initialWetMass, maxThrust, country, techPosition, manUnits, albedoModel, attPointing, interpMethodEop
, opsStatus, operator, objectType, areaTypForPc, eopSource, busModel, vmAbsolute, fixedGeomagDst, trajValues, atmosphericModel, fixedY10P7Mean, epochT0, objectDesignator, wetMass, recommendedOdSpan, odEpochElGMAJ, oebParentFrame, areaMaxForPc, rcsMin, manBasis, dcWinOpen, solarRadUncertainty, odMethod, covRefFrame, dcMaxCycles, prevMessageId, useableStartTime, nextMessageId, trajFrameEpoch, originatorPoc, dragCoeff
, trajId, areaAlongOebMin, propagator, originator, sclkOffsetAtEpoch, trajUnits, covValues, timeSystem, trajPrevId, nBodyPertubations, fixedF10P7, covScaleMin, odMaxPredEigMAJ, dcExecStart, owner, reflectance, gm, dcTimePulsePeriod, covPrevId, areaMinForPc, dcTimePulseDuration, tracksAvailable, interpolation, dcRefDir, fixedS10P7Mean, covType, dragConstArea, manPredSource, trajType, nextLeapTaimUtc, reductionTheory
, covFrameEpoch, manDeviceId, fixedGeomagAp, fixedS10P7, manComposition, techAddress, iXX, iXZ, weightedRms, iXY, classification, attControlMode, originatorPosition, previousMessageEpoch, gravityModel, prmMsgLink, odEpochElGINT, trajNextId, iYY, originatorEmail, iYZ, gdop, manufacturer, dcBodyFrame, dataTypes, orbRevNumBasis, obsUsed, dockedWith, startTime, oebMax, srpConstArea, ocmDataElements, areaAlongOebInt, so
lveN, solveStates, iZZ, manPrevEpoch, odPrevId, dcExecStop, orbAveraging, considerParams, trajRefFrame, vmApparentMax, equatorialRadius, daysSinceFirstObs, interpolationDegree, techPoc, covNextId, srpModel, techPhone, fixedF10P7Mean, attActuatorType, considerN, odEpochElGMIN, rcsMax, timeSpan, oceanTidesModel, daysSinceLastObs, odConfidence, odMaxPredEigMIN, dcWinClose, messageId, centralBodyRotation, creationDate,
 admMsgLink, catalogName, fixedM10P7, manValues, attControl, manFrameEpoch, manRefFrame, rdmMsgLink, centerName, swDataEpoch, covBasis, odEpoch, sclkSecPerSiSec, attKnowledge, shadowBodies, stopTime, covScaleMax, covId, odId, obsAvailable, covConfidence, maxObsGap, useableStopTime, sensors, manPrevId, albedoGridSize, areaAlongOebMax, objectName, user, vmApparent, dvRemaining, techEmail, cdmMsgLink, oebQ3, oebQ2, oe
bQ1, oebParentFrameEpoch, internationalDesignator, nextMessageEpoch, constellation, oebQC, gravAssistName, orbitCategory, dcPaStopAngle, covUnits, techOrg, fixedGeomagKp, shadowModel, oebInt, celestialSource, manNextId, dcRefTime, nextLeapEpoch, swDataSource, trajBasisId, originatorPhone, manId, dragUncertainty, covOrdering, oebMin, originatorAddress, dcMinCycles, tracksUsed, covBasisId, oblateFlattening, sensorsN,
 fixedM10P7Mean, dcBodyTrigger, solarRadCoeff, sedr, dcPaStartAngle, taimUtcAtT0, trajBasis, rcs, vmApparentMin, manBasisId, dcType, avgManeuverFreq, orbRevNum, manPurpose, ut1MUtcAtT0, solidTidesModel, tdmMsgLink, swInterpMethod, alternateNames, fixedY10P7, manNextEpoch, dryMass, dvBol, initialWetMass, maxThrust, country, techPosition, manUnits, albedoModel, attPointing, interpMethodEop, opsStatus, operator, objec
tType, areaTypForPc, eopSource, busModel, vmAbsolute, fixedGeomagDst, trajValues, atmosphericModel, fixedY10P7Mean, epochT0, objectDesignator, wetMass, recommendedOdSpan, odEpochElGMAJ, oebParentFrame, areaMaxForPc, rcsMin, manBasis, dcWinOpen, solarRadUncertainty, odMethod, covRefFrame, dcMaxCycles, prevMessageId, useableStartTime, nextMessageId, trajFrameEpoch, originatorPoc, dragCoeff, trajId, areaAlongOebMin, p
ropagator, originator, sclkOffsetAtEpoch, trajUnits, covValues, timeSystem, trajPrevId, nBodyPertubations, fixedF10P7, covScaleMin, odMaxPredEigMAJ, dcExecStart, owner, reflectance, gm, dcTimePulsePeriod, covPrevId, areaMinForPc, dcTimePulseDuration, tracksAvailable, interpolation, dcRefDir, fixedS10P7Mean, covType, dragConstArea, manPredSource, trajType, nextLeapTaimUtc, reductionTheory, covFrameEpoch, manDeviceId
, fixedGeomagAp, fixedS10P7, manComposition, techAddress, iXX, iXZ, weightedRms, iXY, classification, attControlMode, originatorPosition, previousMessageEpoch, gravityModel, prmMsgLink, odEpochElGINT, trajNextId, iYY, originatorEmail, iYZ, gdop, manufacturer, dcBodyFrame, dataTypes, orbRevNumBasis, obsUsed, dockedWith, startTime, oebMax, srpConstArea, ocmDataElements, areaAlongOebInt, solveN, solveStates, iZZ, manP
revEpoch, odPrevId, dcExecStop, orbAveraging, considerParams, trajRefFrame, vmApparentMax, equatorialRadius, daysSinceFirstObs, interpolationDegree, techPoc, covNextId, srpModel, techPhone, fixedF10P7Mean, attActuatorType, considerN, odEpochElGMIN, rcsMax, timeSpan, oceanTidesModel, daysSinceLastObs, odConfidence, odMaxPredEigMIN, dcWinClose, messageId, centralBodyRotation, creationDate, admMsgLink, catalogName, fixedM10P7, manValues, attControl, manFrameEpoch, manRefFrame, rdmMsgLink, centerName, swDataEpoch, covBasis, odEpoch, sclkSecPerSiSec, attKnowledge, shadowBodies, stopTime, covScaleMax, covId, odId, obsAvailable, covConfidence, maxObsGap, useableStopTime, sensors, manPrevId, albedoGridSize, areaAlongOebMax, objectName, user, vmApparent, dvRemaining, techEmail,
CDM_MSG_LINK, OEB_Q3, OEB_Q2, OEB_Q1, OEB_PARENT_FRAME_EPOCH, INTERNATIONAL_DESIGNATOR, NEXT_MESSAGE_EPOCH, CONSTELLATION, OEB_QC, GRAV_ASSIST_NAME, ORBIT_CATEGORY, DC_PA_STOP_ANGLE, COV_UNITS, TECH_ORG, FIXED_GEOMAG_KP, SHADOW_MODEL, OEB_INT, CELESTIAL_SOURCE, MAN_NEXT_ID, DC_REF_TIME, NEXT_LEAP_EPOCH, SW_DATA_SOURCE, TRAJ_BASIS_ID, ORIGINATOR_PHONE, MAN_ID, DRAG_UNCERTAINTY, COV_ORDERING, OEB_MIN, ORIGINATOR_ADDR
ESS, DC_MIN_CYCLES, TRACKS_USED, COV_BASIS_ID, OBLATE_FLATTENING, SENSORS_N, FIXED_M10P7_MEAN, DC_BODY_TRIGGER, SOLAR_RAD_COEFF, SEDR, DC_PA_START_ANGLE, TAIMUTC_AT_TZERO, TRAJ_BASIS, RCS, VM_APPARENT_MIN, MAN_BASIS_ID, DC_TYPE, AVG_MANEUVER_FREQ, ORB_REVNUM, MAN_PURPOSE, UT1MUTC_AT_TZERO, SOLID_TIDES_MODEL, TDM_MSG_LINK, SW_INTERP_METHOD, ALTERNATE_NAMES, FIXED_Y10P7, MAN_NEXT_EPOCH, DRY_MASS, DV_BOL, INITIAL_WET_
MASS, MAX_THRUST, COUNTRY, TECH_POSITION, MAN_UNITS, ALBEDO_MODEL, ATT_POINTING, INTERP_METHOD_EOP, OPS_STATUS, OPERATOR, OBJECT_TYPE, AREA_TYP_FOR_PC, EOP_SOURCE, BUS_MODEL, VM_ABSOLUTE, FIXED_GEOMAG_DST, TRAJ_VALUES, ATMOSPHERIC_MODEL, FIXED_Y10P7_MEAN, EPOCH_TZERO, OBJECT_DESIGNATOR, WET_MASS, RECOMMENDED_OD_SPAN, OD_EPOCH_EIGMAJ, OEB_PARENT_FRAME, AREA_MAX_FOR_PC, RCS_MIN, MAN_BASIS, DC_WIN_OPEN, SOLAR_RAD_UNCE
RTAINTY, OD_METHOD, COV_REF_FRAME, DC_MAX_CYCLES, PREVIOUS_MESSAGE_ID, USEABLE_START_TIME, NEXT_MESSAGE_ID, TRAJ_FRAME_EPOCH, ORIGINATOR_POC, DRAG_COEFF_NOM, TRAJ_ID, AREA_ALONG_OEB_MIN, PROPAGATOR, ORIGINATOR, SCLK_OFFSET_AT_EPOCH, TRAJ_UNITS, covValues, TIME_SYSTEM, TRAJ_PREV_ID, N_BODY_PERTURBATIONS, FIXED_F10P7, COV_SCALE_MIN, OD_MAX_PRED_EIGMAJ, DC_EXEC_START, OWNER, REFLECTANCE, GM, DC_TIME_PULSE_PERIOD, COV_
PREV_ID, AREA_MIN_FOR_PC, DC_TIME_PULSE_DURATION, TRACKS_AVAILABLE, INTERPOLATION, DC_REF_DIR, FIXED_S10P7_MEAN, COV_TYPE, DRAG_CONST_AREA, MAN_PRED_SOURCE, TRAJ_TYPE, NEXT_LEAP_TAIMUTC, REDUCTION_THEORY, COV_FRAME_EPOCH, MAN_DEVICE_ID, FIXED_GEOMAG_AP, FIXED_S10P7, MAN_COMPOSITION, TECH_ADDRESS, IXX, IXZ, WEIGHTED_RMS, IXY, CLASSIFICATION, ATT_CONTROL_MODE, ORIGINATOR_POSITION, PREVIOUS_MESSAGE_EPOCH, GRAVITY_MODE
L, PRM_MSG_LINK, OD_EPOCH_EIGINT, TRAJ_NEXT_ID, IYY, ORIGINATOR_EMAIL, IYZ, GDOP, MANUFACTURER, DC_BODY_FRAME, DATA_TYPES, ORB_REVNUM_BASIS, OBS_USED, DOCKED_WITH, START_TIME, OEB_MAX, SRP_CONST_AREA, OCM_DATA_ELEMENTS, AREA_ALONG_OEB_INT, SOLVE_N, SOLVE_STATES, IZZ, MAN_PREV_EPOCH, OD_PREV_ID, DC_EXEC_STOP, ORB_AVERAGING, CONSIDER_PARAMS, TRAJ_REF_FRAME, VM_APPARENT_MAX, EQUATORIAL_RADIUS, DAYS_SINCE_FIRST_OBS, IN
TERPOLATION_DEGREE, TECH_POC, COV_NEXT_ID, SRP_MODEL, TECH_PHONE, FIXED_F10P7_MEAN, ATT_ACTUATOR_TYPE, CONSIDER_N, OD_EPOCH_EIGMIN, RCS_MAX, TIME_SPAN, OCEAN_TIDES_MODEL, DAYS_SINCE_LAST_OBS, OD_CONFIDENCE, OD_MIN_PRED_EIGMIN, DC_WIN_CLOSE, MESSAGE_ID, CENTRAL_BODY_ROTATION, CREATION_DATE, ADM_MSG_LINK, CATALOG_NAME, FIXED_M10P7, manValues, ATT_CONTROL, MAN_FRAME_EPOCH, MAN_REF_FRAME, RDM_MSG_LINK, CENTER_NAME, SW_
DATA_EPOCH, COV_BASIS, OD_EPOCH, SCLK_SEC_PER_SI_SEC, ATT_KNOWLEDGE, SHADOW_BODIES, STOP_TIME, COV_SCALE_MAX, COV_ID, OD_ID, OBS_AVAILABLE, COV_CONFIDENCE, MAXIMUM_OBS_GAP, USEABLE_STOP_TIME, SENSORS, MAN_PREV_ID, ALBEDO_GRID_SIZE, AREA_ALONG_OEB_MAX, OBJECT_NAME, USER_DATA, VM_APPARENT, DV_REMAINING, TECH_EMAIL, CDM_MSG_LINK, OEB_Q3, OEB_Q2, OEB_Q1, OEB_PARENT_FRAME_EPOCH, INTERNATIONAL_DESIGNATOR, NEXT_MESSAGE_EP
OCH, CONSTELLATION, OEB_QC, GRAV_ASSIST_NAME, ORBIT_CATEGORY, DC_PA_STOP_ANGLE, COV_UNITS, TECH_ORG, FIXED_GEOMAG_KP, SHADOW_MODEL, OEB_INT, CELESTIAL_SOURCE, MAN_NEXT_ID, DC_REF_TIME, NEXT_LEAP_EPOCH, SW_DATA_SOURCE, TRAJ_BASIS_ID, ORIGINATOR_PHONE, MAN_ID, DRAG_UNCERTAINTY, COV_ORDERING, OEB_MIN, ORIGINATOR_ADDRESS, DC_MIN_CYCLES, TRACKS_USED, COV_BASIS_ID, OBLATE_FLATTENING, SENSORS_N, FIXED_M10P7_MEAN, DC_BODY_
TRIGGER, SOLAR_RAD_COEFF, SEDR, DC_PA_START_ANGLE, TAIMUTC_AT_TZERO, TRAJ_BASIS, RCS, VM_APPARENT_MIN, MAN_BASIS_ID, DC_TYPE, AVG_MANEUVER_FREQ, ORB_REVNUM, MAN_PURPOSE, UT1MUTC_AT_TZERO, SOLID_TIDES_MODEL, TDM_MSG_LINK, SW_INTERP_METHOD, ALTERNATE_NAMES, FIXED_Y10P7, MAN_NEXT_EPOCH, DRY_MASS, DV_BOL, INITIAL_WET_MASS, MAX_THRUST, COUNTRY, TECH_POSITION, MAN_UNITS, ALBEDO_MODEL, ATT_POINTING, INTERP_METHOD_EOP, OPS
_STATUS, OPERATOR, OBJECT_TYPE, AREA_TYP_FOR_PC, EOP_SOURCE, BUS_MODEL, VM_ABSOLUTE, FIXED_GEOMAG_DST, TRAJ_VALUES, ATMOSPHERIC_MODEL, FIXED_Y10P7_MEAN, EPOCH_TZERO, OBJECT_DESIGNATOR, WET_MASS, RECOMMENDED_OD_SPAN, OD_EPOCH_EIGMAJ, OEB_PARENT_FRAME, AREA_MAX_FOR_PC, RCS_MIN, MAN_BASIS, DC_WIN_OPEN, SOLAR_RAD_UNCERTAINTY, OD_METHOD, COV_REF_FRAME, DC_MAX_CYCLES, PREVIOUS_MESSAGE_ID, USEABLE_START_TIME, NEXT_MESSAGE
_ID, TRAJ_FRAME_EPOCH, ORIGINATOR_POC, DRAG_COEFF_NOM, TRAJ_ID, AREA_ALONG_OEB_MIN, PROPAGATOR, ORIGINATOR, SCLK_OFFSET_AT_EPOCH, TRAJ_UNITS, covValues, TIME_SYSTEM, TRAJ_PREV_ID, N_BODY_PERTURBATIONS, FIXED_F10P7, COV_SCALE_MIN, OD_MAX_PRED_EIGMAJ, DC_EXEC_START, OWNER, REFLECTANCE, GM, DC_TIME_PULSE_PERIOD, COV_PREV_ID, AREA_MIN_FOR_PC, DC_TIME_PULSE_DURATION, TRACKS_AVAILABLE, INTERPOLATION, DC_REF_DIR, FIXED_S1
0P7_MEAN, COV_TYPE, DRAG_CONST_AREA, MAN_PRED_SOURCE, TRAJ_TYPE, NEXT_LEAP_TAIMUTC, REDUCTION_THEORY, COV_FRAME_EPOCH, MAN_DEVICE_ID, FIXED_GEOMAG_AP, FIXED_S10P7, MAN_COMPOSITION, TECH_ADDRESS, IXX, IXZ, WEIGHTED_RMS, IXY, CLASSIFICATION, ATT_CONTROL_MODE, ORIGINATOR_POSITION, PREVIOUS_MESSAGE_EPOCH, GRAVITY_MODEL, PRM_MSG_LINK, OD_EPOCH_EIGINT, TRAJ_NEXT_ID, IYY, ORIGINATOR_EMAIL, IYZ, GDOP, MANUFACTURER, DC_BODY
_FRAME, DATA_TYPES, ORB_REVNUM_BASIS, OBS_USED, DOCKED_WITH, START_TIME, OEB_MAX, SRP_CONST_AREA, OCM_DATA_ELEMENTS, AREA_ALONG_OEB_INT, SOLVE_N, SOLVE_STATES, IZZ, MAN_PREV_EPOCH, OD_PREV_ID, DC_EXEC_STOP, ORB_AVERAGING, CONSIDER_PARAMS, TRAJ_REF_FRAME, VM_APPARENT_MAX, EQUATORIAL_RADIUS, DAYS_SINCE_FIRST_OBS, INTERPOLATION_DEGREE, TECH_POC, COV_NEXT_ID, SRP_MODEL, TECH_PHONE, FIXED_F10P7_MEAN, ATT_ACTUATOR_TYPE, 
CONSIDER_N, OD_EPOCH_EIGMIN, RCS_MAX, TIME_SPAN, OCEAN_TIDES_MODEL, DAYS_SINCE_LAST_OBS, OD_CONFIDENCE, OD_MIN_PRED_EIGMIN, DC_WIN_CLOSE, MESSAGE_ID, CENTRAL_BODY_ROTATION, CREATION_DATE, ADM_MSG_LINK, CATALOG_NAME, FIXED_M10P7, manValues, ATT_CONTROL, MAN_FRAME_EPOCH, MAN_REF_FRAME, RDM_MSG_LINK, CENTER_NAME, SW_DATA_EPOCH, COV_BASIS, OD_EPOCH, SCLK_SEC_PER_SI_SEC, ATT_KNOWLEDGE, SHADOW_BODIES, STOP_TIME, COV_SCALE_MAX, COV_ID, OD_ID, OBS_AVAILABLE, COV_CONFIDENCE, MAXIMUM_OBS_GAP, USEABLE_STOP_TIME, SENSORS, MAN_PREV_ID, ALBEDO_GRID_SIZE, AREA_ALONG_OEB_MAX, OBJECT_NAME, USER_DATA, VM_APPARENT, DV_REMAINING, TECH_EMAIL
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — Page number for the queried OCM(s). Default is 0
    
</dd>
</dl>

<dl>
<dd>

**size:** `typing.Optional[int]` — Number of OCM(s) per page.  Max is 10
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.metadata.ocm.<a href="src/tracss/metadata/ocm/client.py">list_by_operational_batch_v1</a>(...) -> typing.List[OperationalOnDemandBatchDto]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve one or more On Demand Batches.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.metadata.ocm.list_by_operational_batch_v1(
    message_id="000043928_conj_000054603_2024329195621",
    batch_id="opebe5bc-95e9-4b11-9594-5d0c61e0b241",
    upload_date=">2024-09-04T18:37:01Z",
    usable_start_time=">2024-09-04T18:37:01Z",
    usable_stop_time=">2024-09-04T18:37:01Z",
    creation_date=">2024-09-04T18:37:01Z",
    created_by="all",
    sort="satNo,ASC",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**message_id:** `typing.Optional[str]` — Message Id (generated) from ASW that processed the CDM during super combo processing. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**batch_id:** `typing.Optional[str]` — Batch Id from the batch of OCMs that was uploaded. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**sat_no:** `typing.Optional[str]` — SatNo from the OCM that was uploaded as part of the batch. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**upload_date:** `typing.Optional[str]` — Upload Date from the OCM batch that was uploaded. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), and Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**usable_start_time:** `typing.Optional[str]` — usableStartTime from an OCM that was uploaded as part of the batch. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), and Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**usable_stop_time:** `typing.Optional[str]` — usableStopTime from an OCM that was uploaded as part of the batch. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), and Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**creation_date:** `typing.Optional[str]` — creationDate from an OCM that was uploaded as part of the batch. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), and Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**cdm_found:** `typing.Optional[str]` — If a cdm is found as part of the batch on-demand run. Valid operators are: Not Equal (<>Value)
    
</dd>
</dl>

<dl>
<dd>

**created_by:** `typing.Optional[str]` — Username of batches to find. Can be a specific username or 'all' for all users. Defaults to requesting user's username
    
</dd>
</dl>

<dl>
<dd>

**sort:** `typing.Optional[str]` — Desired sort field and direction (Ascending = ASC, Descending = DESC), separated by a comma.
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — Page number for the queried TraCSS CDM(s). Default is 0
    
</dd>
</dl>

<dl>
<dd>

**size:** `typing.Optional[int]` — Number of TraCSS CDMs per page.  Max is 100000
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Metadata TracssCat
<details><summary><code>client.metadata.tracss_cat.<a href="src/tracss/metadata/tracss_cat/client.py">upload_csv</a>() -> typing.Any</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Upload a CSV file to update the TraCSS catalog. The CSV must include a noradId column as the minimum required header; all other fields are optional. Rows with noradIds your organization does not own will generate change requests pending TraCSS Operations approval. See tracss.gov for the full list of valid fields and accepted date formats.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.metadata.tracss_cat.upload_csv()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.metadata.tracss_cat.<a href="src/tracss/metadata/tracss_cat/client.py">list</a>(...) -> ListTracssCatResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve one or more TraCSSCats based on query parameters. <b>All fields may be pre-pended with the following optional operators</b>: <br>Equal - (=Value) This is default and does not need to be included.
<br>Not Equal (<>Value)
<br>Greater Than (>Value)
<br>Greater Than or Equal (>=Value)
<br>Less Than (<Value)
<br>Less Than or Equal (<=Value)
<br>Like (\*Value)
<br>Not Like(~*Value)
<p>Search parameters can also be a single value, or the following for searching a list or between values:
<br>In (Value1,Value2) (list of comma separated values)
<br>Between (Value1...Value2) (smaller value first)
<br>
<p>Note that if the field value is a String, it will perform a lexicographical comparison so operators like Less Than on Strings
may return undesired results.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.metadata.tracss_cat.list(
    norad_id="30580, or 30580,30581",
    satellite_name="THEMIS A",
    organization="nasa, or nasa,iridium",
    object_type="Payload",
    fields="noradId,objectType",
    sort="noradId,ASC",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**norad_id:** `typing.Optional[str]` — Norad ID, or list of comma separated ids, of the TracssCat object(s). A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value), In (Value1,Value2) , Between (Value1...Value2) (smaller value first), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**satellite_name:** `typing.Optional[str]` — Name of the TracssCat object. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2) , Between (Value1...Value2) (smaller value first), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**organization:** `typing.Optional[str]` — Organization name, or list of comma separated organization names, responsible for the TracssCat object. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2) , Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object_type:** `typing.Optional[str]` — Object Type of the TracssCat(s) object. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2) , Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**orbital_regime:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**count_only:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**fields:** `typing.Optional[str]` — a comma separated list of fields to return a limited TraCSSCAT object
    
</dd>
</dl>

<dl>
<dd>

**headers_only:** `typing.Optional[bool]` — return only key fields from tracsscat in json format. Does not work with any filters
    
</dd>
</dl>

<dl>
<dd>

**sort:** `typing.Optional[str]` — Desired sort field and direction (Ascending = ASC, Descending = DESC), separated by a comma.
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — Page number for the queried TraCSSCat objects. Default is 0
    
</dd>
</dl>

<dl>
<dd>

**size:** `typing.Optional[int]` — Number of TraCSSCats per page.  Max is 5000
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Metadata Cdm
<details><summary><code>client.metadata.cdm.<a href="src/tracss/metadata/cdm/client.py">list</a>(...) -> ListCdmResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve one or more TraCSS CDMs from TRACSS.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.metadata.cdm.list(
    message_id="000043928_conj_000054603_2024329195621, or 000060681_conj_000026126_2025191132238_1751813630,000060681_conj_000026126_2025191132238_1751898521",
    correlation_id="dd8c054b-6bea-48fb-a245-6cb23331b156",
    ca_status="complete",
    ocm_message_id="000043928_conj_000054603_2024329195621",
    operator_organization="SpaceX",
    tca="2024-314T07:41:39.411",
    creation_date="2024-09-04T18:37:01Z",
    message_for="IRIDIUM 161",
    miss_distance="1000, <500",
    screen_volume_shape="Box, Ellipsoid",
    object1type="Payload",
    object1international_designator="2019-002A",
    object1operator_organization="Iridium",
    object1ephemeris_name="NONE",
    object2type="Payload",
    object2international_designator="2019-002A",
    object2operator_organization="Iridium",
    object2ephemeris_name="NONE",
    conjunction_id="000005e5-d1dd-4a43-b2df-86196e42d29a, or 000005e5-d1dd-4a43-b2df-86196e42d29a,000005e5-d1dd-4a43-b2df-86196e42d29a",
    batch_id="000005e5-d1dd-4a43-b2df-86196e42d29a, or 000005e5-d1dd-4a43-b2df-86196e42d29a,000005e5-d1dd-4a43-b2df-86196e42d29a",
    counter="1000, <500",
    format="json",
    sort="object1ObjectDesignator,ASC",
    fields="object1ObjectDesignator,object2ObjectDesignator",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**message_id:** `typing.Optional[str]` — Message Id (generated), or list of comma separated IDs, from ASW that processed the CDM during super combo processing. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**correlation_id:** `typing.Optional[str]` — Correlation Id (UUID) of the TraCSS CDM. If set to 'most_recent', the most recent CA run's correlationId will be used, and will default to most_recent if not other params used.A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**ca_status:** `typing.Optional[str]` — Can be set to 'Complete' (case insensitive) in conjunction with correlationId to find the latest correlationId of a completed CA run.A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value)
    
</dd>
</dl>

<dl>
<dd>

**ocm_message_id:** `typing.Optional[str]` — OCM Message Id from an OCM that processed the CDM during super combo processing. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1id:** `typing.Optional[str]` — DEPRECATED: Please use object1ObjectDesignator param instead. Object1 Id (Primary Satellite Number). A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value), In (Value1,Value2) , Between (Value1...Value2) (smaller value first), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2id:** `typing.Optional[str]` — DEPRECATED: Please use object2ObjectDesignator param instead. Object2 Id (Secondary Satellite Number of conjuncting satellite). A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value), In (Value1,Value2), Between (Value1...Value2) (smaller value first), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**operator_organization:** `typing.Optional[str]` — The name of the current operator's organization. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**tca:** `typing.Optional[str]` — TCA (Time of Closest Approach). A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value) and Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**creation_date:** `typing.Optional[str]` — Creation Date of the CDM. A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value) and Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**message_for:** `typing.Optional[str]` — Name of Satellite whom the TraCSS cdm is for. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**miss_distance:** `typing.Optional[str]` — The distance (in m) that object1 and object2 missed by. A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value), In (Value1,Value2) , Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**collision_probability:** `typing.Optional[str]` — The probability of object1 and object2 having a collision. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value), In (Value1,Value2) , Between (Value1...Value2) (smaller value first). Does NOT work with Like (\*Value) and Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**screen_volume_shape:** `typing.Optional[str]` — The shape of the screen volume for primary or secondary sat. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1type:** `typing.Optional[str]` — The object type of object1. Possible values are: PAYLOAD, ROCKET BODY, DEBRIS, UNKNOWN, OTHER. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1object_designator:** `typing.Optional[str]` — The designator for object1. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1international_designator:** `typing.Optional[str]` — The international designator for object1. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1operator_organization:** `typing.Optional[str]` — The operator organization for object1. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1ephemeris_name:** `typing.Optional[str]` — The ephemeris name for object1. If an OCM was involved, this will be the OCMs messageId, otherwise NONE. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2type:** `typing.Optional[str]` — The object type of object2. Possible values are: PAYLOAD, ROCKET BODY, DEBRIS, UNKNOWN, OTHER. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2object_designator:** `typing.Optional[str]` — The designator for object2. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2international_designator:** `typing.Optional[str]` — The international designator for object2. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2operator_organization:** `typing.Optional[str]` — The operator organization for object2. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2ephemeris_name:** `typing.Optional[str]` — The ephemeris name for object2. If an OCM was involved, this will be the OCMs messageId, otherwise NONE. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**conjunction_id:** `typing.Optional[str]` — Conjunction ID for a TracssCdm.  This can be a single ID or a comma separated list of IDs. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**batch_id:** `typing.Optional[str]` — Batch ID of an On-Demand CA run. Does not work along with correlationId, and will override this param.A value with an optional operator that may be pre-pended to the value. Valid operators are: In (Value1,Value2)
    
</dd>
</dl>

<dl>
<dd>

**active_cdms_only:** `typing.Optional[bool]` — If true, only active (tca > now) CDMS will be returned.  If false, all CDMS will be returned. If used with latestCdmsOnly then only countOnly and object1ObjectDesignator may be used
    
</dd>
</dl>

<dl>
<dd>

**latest_cdms_only:** `typing.Optional[bool]` — If true, only the latest CDM for obj1 + obj2 combo will be returned.  If false, all CDMS will be returned. Can only be used with countOnly, activeCdmsOnly, object1ObjectDesignator or by itself. Does not work in conjunction with counter param. NOTE: This param can take significantly longer to return data
    
</dd>
</dl>

<dl>
<dd>

**counter:** `typing.Optional[str]` — The counter for the record in the database. Does not work with latestCdmsOnly. A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value), In (Value1,Value2) , Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**headers_only:** `typing.Optional[str]` — Only get the header key fields of the object being asked for. Default is false. If set to true, format will be overwritten to JSON. Does not work with any filters
    
</dd>
</dl>

<dl>
<dd>

**high_alert_only:** `typing.Optional[bool]` — Only get CDMs that met alertable criteria at time of saving
    
</dd>
</dl>

<dl>
<dd>

**format:** `typing.Optional[str]` — Desired format of the returned TraCSS CDM(s). Options are KVN (Default), JSON, XML, or CSV. CSV is a comma separated file derived from KVN
    
</dd>
</dl>

<dl>
<dd>

**sort:** `typing.Optional[str]` — Desired sort field and direction (Ascending = ASC, Descending = DESC), separated by a comma.
    
</dd>
</dl>

<dl>
<dd>

**fields:** `typing.Optional[str]` — Comma separated list of specific fields to include in the response.  Valid fields for JSON and XML are: CORRELATION_ID, TRACSS_CDM_VERS, CLASSIFICATION, CREATION_DATE, ORIGINATOR, MESSAGE_FOR, MESSAGE_ID, CONJUNCTION_ID, TCA, MISS_DISTANCE, MISS_DISTANCE_UNIT, MAHALANOBIS_DISTANCE, MAHALANOBIS_DISTANCE_UNIT, RELATIVE_SPEED, RELATIVE_SPEED_UNIT, RELATIVE_POSITION_R, RELATIVE_POSITION_R_UNIT, RELATIVE_POSITION_T, RELATIVE_POSITION_T_UNIT, RELATIVE_POSITION_N, RELATIVE_POSITION_N_UNIT, RELATIVE_VELOCITY_R, RELATIVE_VELOCITY_R_UNIT, RELATIVE_VELOCITY_T, RELATIVE_VELOCITY_T_UNIT, RELATIVE_VELOCITY_N, RELATIVE_VELOCITY_N_UNIT, APPROACH_ANGLE, APPROACH_ANGLE_UNIT, START_SCREEN_PERIOD, STOP_SCREEN_PERIOD, SCREEN_VOLUME_FRAME, SCREEN_VOLUME_SHAPE, SCREEN_VOLUME_X, SCREEN_VOLUME_X_UNIT, SCREEN_VOLUME_Y, SCREEN_VOLUME_Y_UNIT, SCREEN_VOLUME_Z, SCREEN_VOLUME_Z_UNIT, COLLISION_PROBABILITY, COLLISION_PROBABILITY_METHOD, COLLISION_MAX_PROBABILITY, COLLISION_MAX_PC_METHOD, SAT1_OBJECT, SAT1_OBJECT_DESIGNATOR, SAT1_CATALOG_NAME, SAT1_OBJECT_NAME, SAT1_INTERNATIONAL_DESIGNATOR, SAT1_OBJECT_TYPE, SAT1_OPS_STATUS, SAT1_OPERATOR_ORGANIZATION, SAT1_OPERATOR_PHONE, SAT1_OPERATOR_EMAIL, SAT1_EPHEMERIS_NAME, SAT1_COVARIANCE_METHOD, SAT1_MANEUVERABLE, SAT1_ORBIT_CENTER, SAT1_REF_FRAME, SAT1_GRAVITY_MODEL, SAT1_ATMOSPHERIC_MODEL, SAT1_N_BODY_PERTURBATIONS, SAT1_SOLAR_RAD_PRESSURE, SAT1_EARTH_TIDES, SAT1_INTRACK_THRUST, SAT1_TIME_LASTOB_START, SAT1_TIME_LASTOB_END, SAT1_RECOMMENDED_OD_SPAN, SAT1_RECOMMENDED_OD_SPAN_UNIT, SAT1_ACTUAL_OD_SPAN, SAT1_ACTUAL_OD_SPAN_UNIT, SAT1_OBS_AVAILABLE, SAT1_OBS_USED, SAT1_TRACKS_AVAILABLE, SAT1_TRACKS_USED, SAT1_RESIDUALS_ACCEPTED, SAT1_RESIDUALS_ACCEPTED_UNIT, SAT1_WEIGHTED_RMS, SAT1_AREA_PC, SAT1_AREA_PC_UNIT, SAT1_MASS, SAT1_MASS_UNIT, SAT1_HBR, SAT1_HBR_UNIT, SAT1_CD_AREA_OVER_MASS, SAT1_CD_AREA_OVER_MASS_UNIT, SAT1_CR_AREA_OVER_MASS, SAT1_CR_AREA_OVER_MASS_UNIT, SAT1_THRUST_ACCELERATION, SAT1_THRUST_ACCELERATION_UNIT, SAT1_SEDR, SAT1_SEDR_UNIT, SAT1_APOAPSIS_ALTITUDE, SAT1_APOAPSIS_ALTITUDE_UNIT, SAT1_PERIAPSIS_ALTITUDE, SAT1_PERIAPSIS_ALTITUDE_UNIT, SAT1_INCLINATION, SAT1_INCLINATION_UNIT, SAT1_X, SAT1_X_UNIT, SAT1_Y, SAT1_Y_UNIT, SAT1_Z, SAT1_Z_UNIT, SAT1_X_DOT, SAT1_X_DOT_UNIT, SAT1_Y_DOT, SAT1_Y_DOT_UNIT, SAT1_Z_DOT, SAT1_Z_DOT_UNIT, SAT2_OBJECT, SAT2_OBJECT_DESIGNATOR, SAT2_CATALOG_NAME, SAT2_OBJECT_NAME, SAT2_INTERNATIONAL_DESIGNATOR, SAT2_OBJECT_TYPE, SAT2_OPS_STATUS, SAT2_OPERATOR_ORGANIZATION, SAT2_OPERATOR_PHONE, SAT2_OPERATOR_EMAIL, SAT2_EPHEMERIS_NAME, SAT2_COVARIANCE_METHOD, SAT2_MANEUVERABLE, SAT2_ORBIT_CENTER, SAT2_REF_FRAME, SAT2_GRAVITY_MODEL, SAT2_ATMOSPHERIC_MODEL, SAT2_N_BODY_PERTURBATIONS, SAT2_SOLAR_RAD_PRESSURE, SAT2_EARTH_TIDES, SAT2_INTRACK_THRUST, SAT2_TIME_LASTOB_START, SAT2_TIME_LASTOB_END, SAT2_RECOMMENDED_OD_SPAN, SAT2_RECOMMENDED_OD_SPAN_UNIT, SAT2_ACTUAL_OD_SPAN, SAT2_ACTUAL_OD_SPAN_UNIT, SAT2_OBS_AVAILABLE, SAT2_OBS_USED, SAT2_TRACKS_AVAILABLE, SAT2_TRACKS_USED, SAT2_RESIDUALS_ACCEPTED, SAT2_RESIDUALS_ACCEPTED_UNIT, SAT2_WEIGHTED_RMS, SAT2_AREA_PC, SAT2_AREA_PC_UNIT, SAT2_MASS, SAT2_MASS_UNIT, SAT2_HBR, SAT2_HBR_UNIT, SAT2_CD_AREA_OVER_MASS, SAT2_CD_AREA_OVER_MASS_UNIT, SAT2_CR_AREA_OVER_MASS, SAT2_CR_AREA_OVER_MASS_UNIT, SAT2_THRUST_ACCELERATION, SAT2_THRUST_ACCELERATION_UNIT, SAT2_SEDR, SAT2_SEDR_UNIT, SAT2_APOAPSIS_ALTITUDE, SAT2_APOAPSIS_ALTITUDE_UNIT, SAT2_PERIAPSIS_ALTITUDE, SAT2_PERIAPSIS_ALTITUDE_UNIT, SAT2_INCLINATION, SAT2_INCLINATION_UNIT, SAT2_X, SAT2_X_UNIT, SAT2_Y, SAT2_Y_UNIT, SAT2_Z, SAT2_Z_UNIT, SAT2_X_DOT, SAT2_X_DOT_UNIT, SAT2_Y_DOT, SAT2_Y_DOT_UNIT, SAT2_Z_DOT, SAT2_Z_DOT_UNIT, USER_DEFINED_MEETS_ALERTABLE_CRITERIA, USER_DEFINED_RUN_ID, USER_DEFINED_CORRELATION_ID, USER_DEFINED_DILUTION_STATUS, USER_DEFINED_DILUTION_SIGNIFICANCE, USER_DEFINED_ENVIRONMENTAL_IMPACT_FRAGMENTATION, USER_DEFINED_FRAGMENTATION_MODEL
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — Page number for the queried TraCSS CDM(s). Default is 0
    
</dd>
</dl>

<dl>
<dd>

**size:** `typing.Optional[int]` — Number of TraCSS CDMs per page.  Max is 5000
    
</dd>
</dl>

<dl>
<dd>

**count_only:** `typing.Optional[bool]` — If true, only the count of the TraCSS CDMs will be returned. Default is false.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.metadata.cdm.<a href="src/tracss/metadata/cdm/client.py">list_by_operational_batch</a>(...) -> ListByOperationalBatchCdmResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve one or more TraCSS CDMs for an On-Demand run.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.metadata.cdm.list_by_operational_batch(
    batch_id="ope76b2e-2e2f-4526-b782-f96d2675ec32",
    format="KVN",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**batch_id:** `str` — Batch Id (generated) from an upload of OCMs for operational On Demand Screening. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**headers_only:** `typing.Optional[str]` — Only get the header key fields of the object being asked for. Default is false. If set to true, format will be overwritten to JSON
    
</dd>
</dl>

<dl>
<dd>

**format:** `typing.Optional[str]` — format of the TraCSS CDM. Valid values are KVN, JSON, or XML. Default if not provided is KVN. Valid operators are: Equal (=value)
    
</dd>
</dl>

<dl>
<dd>

**size:** `typing.Optional[int]` — Number of TraCSS CDMs per page.  Max is 100000
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.metadata.cdm.<a href="src/tracss/metadata/cdm/client.py">list_v1</a>(...) -> ListV1CdmResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve one or more TraCSS CDMs from TRACSS.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.metadata.cdm.list_v1(
    message_id="000043928_conj_000054603_2024329195621, or 000060681_conj_000026126_2025191132238_1751813630,000060681_conj_000026126_2025191132238_1751898521",
    correlation_id="dd8c054b-6bea-48fb-a245-6cb23331b156",
    ca_status="complete",
    ocm_message_id="000043928_conj_000054603_2024329195621",
    operator_organization="SpaceX",
    tca="2024-314T07:41:39.411",
    creation_date="2024-09-04T18:37:01Z",
    message_for="IRIDIUM 161",
    miss_distance="1000, <500",
    screening_option="Covariance",
    object1screen_volume_shape="Box, Ellipsoid",
    object1type="Payload",
    object1international_designator="2019-002A",
    object1operator_organization="Iridium",
    object1ephemeris_name="NONE",
    object2screen_volume_shape="Box, Ellipsoid",
    object2type="Payload",
    object2international_designator="2019-002A",
    object2operator_organization="Iridium",
    object2ephemeris_name="NONE",
    conjunction_id="000005e5-d1dd-4a43-b2df-86196e42d29a, or 000005e5-d1dd-4a43-b2df-86196e42d29a,000005e5-d1dd-4a43-b2df-86196e42d29a",
    batch_id="000005e5-d1dd-4a43-b2df-86196e42d29a, or 000005e5-d1dd-4a43-b2df-86196e42d29a,000005e5-d1dd-4a43-b2df-86196e42d29a",
    counter="1000, <500",
    format="json",
    sort="object1ObjectDesignator,ASC",
    fields="Comma separated list of fields to include in the response.",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**message_id:** `typing.Optional[str]` — Message Id (generated), or list of comma separated IDs, from ASW that processed the CDM during super combo processing. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**correlation_id:** `typing.Optional[str]` — Correlation Id (UUID) of the TraCSS CDM. If set to 'most_recent', the most recent CA run's correlationId will be used, and will default to most_recent if not other params used.A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**ca_status:** `typing.Optional[str]` — Can be set to 'Complete' (case insensitive) in conjunction with correlationId to find the latest correlationId of a completed CA run.A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value)
    
</dd>
</dl>

<dl>
<dd>

**ocm_message_id:** `typing.Optional[str]` — OCM Message Id from an OCM that processed the CDM during super combo processing. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1id:** `typing.Optional[str]` — DEPRECATED: Please use object1ObjectDesignator param instead. Object1 Id (Primary Satellite Number). A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value), In (Value1,Value2) , Between (Value1...Value2) (smaller value first), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2id:** `typing.Optional[str]` — DEPRECATED: Please use object2ObjectDesignator param instead. Object2 Id (Secondary Satellite Number of conjuncting satellite). A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value), In (Value1,Value2), Between (Value1...Value2) (smaller value first), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**operator_organization:** `typing.Optional[str]` — The name of the current operator's organization. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**tca:** `typing.Optional[str]` — TCA (Time of Closest Approach). A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value) and Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**creation_date:** `typing.Optional[str]` — Creation Date of the CDM. A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value) and Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**message_for:** `typing.Optional[str]` — Name of Satellite whom the TraCSS cdm is for. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**miss_distance:** `typing.Optional[str]` — The distance (in m) that object1 and object2 missed by. A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value), In (Value1,Value2) , Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**collision_probability:** `typing.Optional[str]` — The probability of object1 and object2 having a collision. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value), In (Value1,Value2) , Between (Value1...Value2) (smaller value first). Does NOT work with Like (\*Value) and Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**screening_option:** `typing.Optional[str]` — What was used during the screening process. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1screen_volume_shape:** `typing.Optional[str]` — The shape of the screen volume for object1. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1type:** `typing.Optional[str]` — The object type of object1. Possible values are: PAYLOAD, ROCKET BODY, DEBRIS, UNKNOWN, OTHER. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1object_designator:** `typing.Optional[str]` — The designator for object1. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1international_designator:** `typing.Optional[str]` — The international designator for object1. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1operator_organization:** `typing.Optional[str]` — The operator organization for object1. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object1ephemeris_name:** `typing.Optional[str]` — The ephemeris name for object1. If an OCM was involved, this will be the OCMs messageId, otherwise NONE. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2screen_volume_shape:** `typing.Optional[str]` — The shape of the screen volume for object2. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2type:** `typing.Optional[str]` — The object type of object2. Possible values are: PAYLOAD, ROCKET BODY, DEBRIS, UNKNOWN, OTHER. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2object_designator:** `typing.Optional[str]` — The designator for object2. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2international_designator:** `typing.Optional[str]` — The international designator for object2. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2operator_organization:** `typing.Optional[str]` — The operator organization for object2. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**object2ephemeris_name:** `typing.Optional[str]` — The ephemeris name for object2. If an OCM was involved, this will be the OCMs messageId, otherwise NONE. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**conjunction_id:** `typing.Optional[str]` — Conjunction ID for a TracssCdm.  This can be a single ID or a comma separated list of IDs. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**batch_id:** `typing.Optional[str]` — Batch ID of an On-Demand CA run. Does not work along with correlationId, and will override this param.A value with an optional operator that may be pre-pended to the value. Valid operators are: In (Value1,Value2)
    
</dd>
</dl>

<dl>
<dd>

**active_cdms_only:** `typing.Optional[bool]` — If true, only active (tca > now) CDMS will be returned. If used with latestCdmsOnly then only countOnly and object1ObjectDesignator may be used.  If false, all CDMS will be returned.Does not work in conjunction with counter param. NOTE: This param can take significantly longer to return data
    
</dd>
</dl>

<dl>
<dd>

**latest_cdms_only:** `typing.Optional[bool]` — If true, only the latest CDM for obj1 + obj2 combo will be returned. Can only be used with countOnly, activeCdmsOnly, object1ObjectDesignator or by itself.  If false, all CDMS will be returned.
    
</dd>
</dl>

<dl>
<dd>

**counter:** `typing.Optional[str]` — The counter for the record in the database. Does not work with latestCdmsOnly. A value with an optional operator that may be pre-pended to the value. Valid operators are: Greater Than (>Value), Less Than (<Value), Greater Than or Equal (>=Value), Less Than or Equal (<=Value), Not Equal (<>Value), In (Value1,Value2) , Between (Value1...Value2) (smaller value first)
    
</dd>
</dl>

<dl>
<dd>

**headers_only:** `typing.Optional[str]` — Only get the header key fields of the object being asked for. Default is false. If set to true, format will be overwritten to JSON. Does not work with any filters
    
</dd>
</dl>

<dl>
<dd>

**format:** `typing.Optional[str]` — Desired format of the returned TraCSS CDM(s). Options are KVN (Default), JSON, XML, or CSV. CSV is a comma separated file derived from KVN
    
</dd>
</dl>

<dl>
<dd>

**sort:** `typing.Optional[str]` — Desired sort field and direction (Ascending = ASC, Descending = DESC), separated by a comma.
    
</dd>
</dl>

<dl>
<dd>

**fields:** `typing.Optional[str]` — Comma separated list of specific fields to include in the response.  Valid fields for JSON and XML are: CORRELATION_ID, CCSDS_CDM_VERS, COMMENT, CREATION_DATE, ORIGINATOR, MESSAGE_FOR, MESSAGE_ID, TCA, MISS_DISTANCE, MISS_DISTANCE_UNIT, RELATIVE_SPEED, RELATIVE_SPEED_UNIT, RELATIVE_POSITION_R, RELATIVE_POSITION_R_UNIT, RELATIVE_POSITION_T, RELATIVE_POSITION_T_UNIT, RELATIVE_POSITION_N, RELATIVE_POSITION_N_UNIT, RELATIVE_VELOCITY_R, RELATIVE_VELOCITY_R_UNIT, RELATIVE_VELOCITY_T, RELATIVE_VELOCITY_T_UNIT, RELATIVE_VELOCITY_N, RELATIVE_VELOCITY_N_UNIT, COLLISION_PROBABILITY, COLLISION_PROBABILITY_METHOD, START_SCREEN_PERIOD, STOP_SCREEN_PERIOD, SCREEN_VOLUME_SHAPE, SCREEN_VOLUME_FRAME, SCREEN_VOLUME_X, SCREEN_VOLUME_X_UNIT, SCREEN_VOLUME_Y, SCREEN_VOLUME_Y_UNIT, SCREEN_VOLUME_Z, SCREEN_VOLUME_Z_UNIT, SCREEN_ENTRY_TIME, SCREEN_EXIT_TIME, SAT1_OBJECT_DESIGNATOR, SAT1_CATALOG_NAME, SAT1_OBJECT_NAME, SAT1_INTERNATIONAL_DESIGNATOR, SAT1_OBJECT_TYPE, SAT1_OPERATOR_CONTACT_POSITION, SAT1_OPERATOR_ORGANIZATION, SAT1_OPERATOR_PHONE, SAT1_OPERATOR_EMAIL, SAT1_EPHEMERIS_NAME, SAT1_COVARIANCE_METHOD, SAT1_MANEUVERABLE, SAT1_ORBIT_CENTER, SAT1_REF_FRAME, SAT1_GRAVITY_MODEL, SAT1_ATMOSPHERIC_MODEL, SAT1_N_BODY_PERTURBATIONS, SAT1_SOLAR_RAD_PRESSURE, SAT1_EARTH_TIDES, SAT1_INTRACK_THRUST, SAT1_TIME_LASTOB_START, SAT1_TIME_LASTOB_END, SAT1_RECOMMENDED_OD_SPAN, SAT1_RECOMMENDED_OD_SPAN_UNIT, SAT1_ACTUAL_OD_SPAN, SAT1_ACTUAL_OD_SPAN_UNIT, SAT1_OBS_AVAILABLE, SAT1_OBS_USED, SAT1_TRACKS_AVAILABLE, SAT1_TRACKS_USED, SAT1_RESIDUALS_ACCEPTED, SAT1_RESIDUALS_ACCEPTED_UNIT, SAT1_WEIGHTED_RMS, SAT1_AREA_PC, SAT1_AREA_PC_UNIT, SAT1_CD_AREA_OVER_MASS, SAT1_CD_AREA_OVER_MASS_UNIT, SAT1_CR_AREA_OVER_MASS, SAT1_CR_AREA_OVER_MASS_UNIT, SAT1_THRUST_ACCELERATION, SAT1_THRUST_ACCELERATION_UNIT, SAT1_SEDR, SAT1_SEDR_UNIT, SAT1_X, SAT1_X_UNIT, SAT1_Y, SAT1_Y_UNIT, SAT1_Z, SAT1_Z_UNIT, SAT1_X_DOT, SAT1_X_DOT_UNIT, SAT1_Y_DOT, SAT1_Y_DOT_UNIT, SAT1_Z_DOT, SAT1_Z_DOT_UNIT, SAT2_OBJECT_DESIGNATOR, SAT2_CATALOG_NAME, SAT2_OBJECT_NAME, SAT2_INTERNATIONAL_DESIGNATOR, SAT2_OBJECT_TYPE, SAT2_OPERATOR_CONTACT_POSITION, SAT2_OPERATOR_ORGANIZATION, SAT2_OPERATOR_PHONE, SAT2_OPERATOR_EMAIL, SAT2_EPHEMERIS_NAME, SAT2_COVARIANCE_METHOD, SAT2_MANEUVERABLE, SAT2_ORBIT_CENTER, SAT2_REF_FRAME, SAT2_GRAVITY_MODEL, SAT2_ATMOSPHERIC_MODEL, SAT2_N_BODY_PERTURBATIONS, SAT2_SOLAR_RAD_PRESSURE, SAT2_EARTH_TIDES, SAT2_INTRACK_THRUST, SAT2_TIME_LASTOB_START, SAT2_TIME_LASTOB_END, SAT2_RECOMMENDED_OD_SPAN, SAT2_RECOMMENDED_OD_SPAN_UNIT, SAT2_ACTUAL_OD_SPAN, SAT2_ACTUAL_OD_SPAN_UNIT, SAT2_OBS_AVAILABLE, SAT2_OBS_USED, SAT2_TRACKS_AVAILABLE, SAT2_TRACKS_USED, SAT2_RESIDUALS_ACCEPTED, SAT2_RESIDUALS_ACCEPTED_UNIT, SAT2_WEIGHTED_RMS, SAT2_AREA_PC, SAT2_AREA_PC_UNIT, SAT2_CD_AREA_OVER_MASS, SAT2_CD_AREA_OVER_MASS_UNIT, SAT2_CR_AREA_OVER_MASS, SAT2_CR_AREA_OVER_MASS_UNIT, SAT2_THRUST_ACCELERATION, SAT2_THRUST_ACCELERATION_UNIT, SAT2_SEDR, SAT2_SEDR_UNIT, SAT2_X, SAT2_X_UNIT, SAT2_Y, SAT2_Y_UNIT, SAT2_Z, SAT2_Z_UNIT, SAT2_X_DOT, SAT2_X_DOT_UNIT, SAT2_Y_DOT, SAT2_Y_DOT_UNIT, SAT2_Z_DOT, SAT2_Z_DOT_UNIT
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — Page number for the queried TraCSS CDM(s). Default is 0
    
</dd>
</dl>

<dl>
<dd>

**size:** `typing.Optional[int]` — Number of TraCSS CDMs per page.  Max is 5000
    
</dd>
</dl>

<dl>
<dd>

**count_only:** `typing.Optional[bool]` — If true, only the count of the TraCSS CDMs will be returned. Default is false.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.metadata.cdm.<a href="src/tracss/metadata/cdm/client.py">list_by_operational_batch_v1</a>(...) -> ListByOperationalBatchV1CdmResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve one or more TraCSS CDMs for an On-Demand run.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.metadata.cdm.list_by_operational_batch_v1(
    batch_id="ope76b2e-2e2f-4526-b782-f96d2675ec32",
    format="KVN",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**batch_id:** `str` — Batch Id (generated) from an upload of OCMs for operational On Demand Screening. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2), Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**headers_only:** `typing.Optional[str]` — Only get the header key fields of the object being asked for. Default is false. If set to true, format will be overwritten to JSON
    
</dd>
</dl>

<dl>
<dd>

**format:** `typing.Optional[str]` — format of the TraCSS CDM. Valid values are KVN, JSON, and XML. Default if not provided is KVN. Valid operators are: Equal (=value)
    
</dd>
</dl>

<dl>
<dd>

**size:** `typing.Optional[int]` — Number of TraCSS CDMs per page.  Max is 100000
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Metadata TipReports
<details><summary><code>client.metadata.tip_reports.<a href="src/tracss/metadata/tip_reports/client.py">list</a>(...) -> typing.Any</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Find all TIP reports in the system or all reports that meet your search criteria defined by the query parameters.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.metadata.tip_reports.list(
    norad_id="noradId=12345",
    id="id=87",
    msg_epoch="msgEpoch=2004-09-28T02:49:00.000Z",
    insert_epoch="insertEpoch=2004-09-28T02:49:00.000Z",
    decay_epoch="decayEpoch=2004-09-28T02:49:00.000Z",
    window="window=900",
    rev="rev=25952",
    direction="direction=descending",
    latitude="latitude=36.0",
    longitude="longitude=217.5",
    inclination="inclination=53.0",
    next_report="decayEpoch=48",
    high_interest="highInterest=Y",
    fields="fields=noradId,id,window,decayEpoch",
    format="json",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**norad_id:** `typing.Optional[str]` — The noradId of an object. Valid operators are: Equal (=Value), Not Equal (=<>Value), Greater Than or Equal (=>=Value), Greater Than (=>Value), Less Than or Equal (=<=Value), Less Than (=<Value), In (=Value1,Value2,etc), Between (=Value1...Value2)
    
</dd>
</dl>

<dl>
<dd>

**id:** `typing.Optional[str]` — The numeric id of the TIP report. Valid operators are: Equal (=Value), Not Equal (=<>Value), Greater Than or Equal (=>=Value), Greater Than (=>Value), Less Than or Equal (=<=Value), Less Than (=<Value), In (=Value1,Value2,etc), Between (=Value1...Value2)
    
</dd>
</dl>

<dl>
<dd>

**msg_epoch:** `typing.Optional[str]` — Timestamp of when of the TIP report was produced. Valid operators are: Equal (=Value), Not Equal (=<>Value), Greater Than or Equal (=>=Value), Greater Than (=>Value), Less Than or Equal (=<=Value), Less Than (=<Value), In (=Value1,Value2,etc), Between (=Value1...Value2)
    
</dd>
</dl>

<dl>
<dd>

**insert_epoch:** `typing.Optional[str]` — Timestamp of when the record was inserted in the system. Valid operators are: Equal (=Value), Not Equal (=<>Value), Greater Than or Equal (=>=Value), Greater Than (=>Value), Less Than or Equal (=<=Value), Less Than (=<Value), In (=Value1,Value2,etc), Between (=Value1...Value2)
    
</dd>
</dl>

<dl>
<dd>

**decay_epoch:** `typing.Optional[str]` — Timestamp of the predicted time of atmospheric re-entry. Valid operators are: Equal (=Value), Not Equal (=<>Value), Greater Than or Equal (=>=Value), Greater Than (=>Value), Less Than or Equal (=<=Value), Less Than (=<Value), In (=Value1,Value2,etc), Between (=Value1...Value2)
    
</dd>
</dl>

<dl>
<dd>

**window:** `typing.Optional[str]` — The uncertainty window around the re-entry time in seconds. Valid operators are: Equal (=Value), Not Equal (=<>Value), Greater Than or Equal (=>=Value), Greater Than (=>Value), Less Than or Equal (=<=Value), Less Than (=<Value), In (=Value1,Value2,etc), Between (=Value1...Value2)
    
</dd>
</dl>

<dl>
<dd>

**rev:** `typing.Optional[str]` — The orbit revolution number at the time of prediction. Valid operators are: Equal (=Value), Not Equal (=<>Value), Greater Than or Equal (=>=Value), Greater Than (=>Value), Less Than or Equal (=<=Value), Less Than (=<Value), In (=Value1,Value2,etc), Between (=Value1...Value2)
    
</dd>
</dl>

<dl>
<dd>

**direction:** `typing.Optional[str]` — The direction of orbital trajectory during re-entry prediction. Valid operators are: Equal (=Value), Not Equal (=<>Value), Like (=*Value), Not Like (=~*Value). Possible values: ascending and descending.
    
</dd>
</dl>

<dl>
<dd>

**latitude:** `typing.Optional[str]` — The latitude of predicted re-entry location. Valid operators are: Equal (=Value), Not Equal (=<>Value), Greater Than or Equal (=>=Value), Greater Than (=>Value), Less Than or Equal (=<=Value), Less Than (=<Value), In (=Value1,Value2,etc), Between (=Value1...Value2)
    
</dd>
</dl>

<dl>
<dd>

**longitude:** `typing.Optional[str]` — Longitude of predicted re-entry location. Valid operators are: Equal (=Value), Not Equal (=<>Value), Greater Than or Equal (=>=Value), Greater Than (=>Value), Less Than or Equal (=<=Value), Less Than (=<Value), In (=Value1,Value2,etc), Between (=Value1...Value2)
    
</dd>
</dl>

<dl>
<dd>

**inclination:** `typing.Optional[str]` — Inclination of the orbit at time of prediction. Valid operators are: Equal (=Value), Not Equal (=<>Value), Greater Than or Equal (=>=Value), Greater Than (=>Value), Less Than or Equal (=<=Value), Less Than (=<Value), In (=Value1,Value2,etc), Between (=Value1...Value2)
    
</dd>
</dl>

<dl>
<dd>

**next_report:** `typing.Optional[str]` — Estimated time in hours until next update (Integer). Valid operators are: Equal (=Value), Not Equal (=<>Value), Greater Than or Equal (=>=Value), Greater Than (=>Value), Less Than or Equal (=<=Value), Less Than (=<Value), In (=Value1,Value2,etc), Between (=Value1...Value2)
    
</dd>
</dl>

<dl>
<dd>

**high_interest:** `typing.Optional[str]` — Flag indicating if object is considered high interest for re-entry tracking. Valid operators are: Equal (=Value), Not Equal (=<>Value), Like (=*Value), Not Like (=~*Value). Possible values: Y, N
    
</dd>
</dl>

<dl>
<dd>

**fields:** `typing.Optional[str]` 

Fields to return from TIP object. Valid fields are: Valid fields for JSON and XML include: NORAD_CAT_ID, MSG_EPOCH, INSERT_EPOCH, DECAY_EPOCH, WINDOW, REV, DIRECTION,
LAT, LON, INCL, NEXT_REPORT, ID, HIGH_INTEREST.
Regular KVN format does not support tuples.
    
</dd>
</dl>

<dl>
<dd>

**format:** `typing.Optional[str]` — Format of the request body. KVN, JSON, and XML are all valid formats. KVN is default.
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — Page number for queried TIP results. Default page is is 0
    
</dd>
</dl>

<dl>
<dd>

**size:** `typing.Optional[int]` — Number of TIP Reports per page.  Max and default value is 2147483647
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Metadata SpaceTrack
<details><summary><code>client.metadata.space_track.<a href="src/tracss/metadata/space_track/client.py">list</a>(...) -> typing.Optional[typing.List[SpaceTrack]]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieves Space-track data based on a given correlationId
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.metadata.space_track.list()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `typing.Optional[str]` — Correlation Id (UUID) of the Space-Track data. If no id is provided, returns the names and correlationIds of all zip files we have received.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.metadata.space_track.<a href="src/tracss/metadata/space_track/client.py">list_nested</a>(...) -> typing.List[SpaceTrackNestedDto]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve Space Track Package Data with all tar files combined in response
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.metadata.space_track.list_nested()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `typing.Optional[str]` — Correlation Id (UUID) of the Space-Track data
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Metadata Schemas
<details><summary><code>client.metadata.schemas.<a href="src/tracss/metadata/schemas/client.py">get_xsd</a>() -> typing.List[str]</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.metadata.schemas.get_xsd()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.metadata.schemas.<a href="src/tracss/metadata/schemas/client.py">get_json</a>() -> typing.List[str]</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.metadata.schemas.get_json()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Metadata ConjunctionEvents
<details><summary><code>client.metadata.conjunction_events.<a href="src/tracss/metadata/conjunction_events/client.py">list</a>(...) -> ListConjunctionEventsResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve one or more Evolving Conjunctions events from TRACSS.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.metadata.conjunction_events.list(
    min_tca="2025-06-03 00:40:26.36",
    max_tca="2025-06-03 00:40:26.36",
    creation_date="2025-05-29 02:56:47.0",
    conjunction_data_event_id="bfd39e92-44e2-4eae-8dac-b6c3e5ecc9e3, or bfd39e92-44e2-4eae-8dac-b6c3e5ecc9e3,8f1400b8-438b-4246-9d52-de6d2728eaac",
    sort="tca",
    sort_direction="desc",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**object1object_designator:** `typing.Optional[str]` — Object1 Id (Primary Satellite Number). can be a comma seperated list
    
</dd>
</dl>

<dl>
<dd>

**object2object_designator:** `typing.Optional[str]` — Object2 Id (Secondary Satellite Number of conjuncting satellite). can be a comma seperated list
    
</dd>
</dl>

<dl>
<dd>

**min_tca:** `typing.Optional[str]` — Minimum TCA (Time of Closest Approach).
    
</dd>
</dl>

<dl>
<dd>

**max_tca:** `typing.Optional[str]` — Maximum TCA (Time of Closest Approach).
    
</dd>
</dl>

<dl>
<dd>

**min_miss_distance:** `typing.Optional[str]` — Minimum miss distance (in meters) of the event
    
</dd>
</dl>

<dl>
<dd>

**max_miss_distance:** `typing.Optional[str]` — Maximum miss distance (in meters) of the event
    
</dd>
</dl>

<dl>
<dd>

**min_collision_probability:** `typing.Optional[str]` — Minimum collision probability of the event
    
</dd>
</dl>

<dl>
<dd>

**max_collision_probability:** `typing.Optional[str]` — Minimum collision probability of the event
    
</dd>
</dl>

<dl>
<dd>

**creation_date:** `typing.Optional[str]` — Date the event was created
    
</dd>
</dl>

<dl>
<dd>

**conjunction_data_event_id:** `typing.Optional[str]` — Conjunction event Id, or comma separated list of IDs, of one or more conjunction events.
    
</dd>
</dl>

<dl>
<dd>

**sort:** `typing.Optional[str]` — Value to sort by, valid values are tca, missDistance, or collisionProbability
    
</dd>
</dl>

<dl>
<dd>

**sort_direction:** `typing.Optional[str]` — direction to sort
    
</dd>
</dl>

<dl>
<dd>

**size:** `typing.Optional[int]` — max number of events returned. Default max is 500000 to avoid to large a query
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — the page you want to retrieve during pagination
    
</dd>
</dl>

<dl>
<dd>

**headers_only:** `typing.Optional[bool]` — returns a reduced object with more necessary data. Does not work with any filters
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Metadata Announcements
<details><summary><code>client.metadata.announcements.<a href="src/tracss/metadata/announcements/client.py">list</a>(...) -> typing.List[SpaceTrackAnnouncement]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Fetches announcement records from the database. Returns a JSON array of announcement objects. Supports optional filtering by ID, type, and pagination.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.metadata.announcements.list(
    id="someOrganizationId",
    announcement_type="INFORMATION",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `typing.Optional[str]` — The ID of the announcement. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2) , Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**announcement_type:** `typing.Optional[str]` — The type of announcement. A value with an optional operator that may be pre-pended to the value. Valid operators are: Not Equal (<>Value), In (Value1,Value2) , Like (\*Value), Not Like(~*Value)
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — Page number for pagination. If no value is entered, the default value is 0.
    
</dd>
</dl>

<dl>
<dd>

**size:** `typing.Optional[int]` — number of results returned. If no value is entered, the default value is 2147483647.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Subscriber Topics
<details><summary><code>client.subscriber.topics.<a href="src/tracss/subscriber/topics/client.py">list</a>() -> str</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve the list of available topics to subscribe to, as well as their latest offset
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.subscriber.topics.list()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.subscriber.topics.<a href="src/tracss/subscriber/topics/client.py">get_offset</a>(...) -> typing.Any</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve the latest kafka offset of a passed in topic
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.subscriber.topics.get_offset(
    topic="gov.tracss.tracss.v1.cdms",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**topic:** `str` — Topic to retrieve the offset from
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Subscriber Messages
<details><summary><code>client.subscriber.messages.<a href="src/tracss/subscriber/messages/client.py">list</a>(...) -> ListMessagesResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve messages from a given topic starting at a given offset. Available topics are:                            gov.tracss.parsed.elsetCsv,                            gov.tracss.tracss.v1.cdms,                            gov.tracss.tracss.v2.cdms,                            gov.tracss.parsed.v1.ocms,                            gov.tracss.parsed.v2.ocms,                            gov.tracss.parsed.spVectors,                            gov.tracss.parsed.tracsscat                            gov.tracss.conjunction.data.event
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from tracss import TraCSS
from tracss.environment import TraCSSEnvironment

client = TraCSS(
    token="<token>",
    environment=TraCSSEnvironment.DEFAULT,
)

client.subscriber.messages.list(
    topic="gov.tracss.tracss.v1.cdms",
    offset="offset",
    fields="missDistance, collisionProbability",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**topic:** `str` — Topic to retrieve messages from
    
</dd>
</dl>

<dl>
<dd>

**offset:** `str` — Offset to begin retrieving messages from - represents the starting point. Defaults to 0
    
</dd>
</dl>

<dl>
<dd>

**max_results:** `typing.Optional[str]` — Optional - max amount of messages to retrieve. If not provided, defaults to 1000, or 25 for gov.tracss.parsed.v1.ocms. This limits the number of results in the response - not number of messages looked at
    
</dd>
</dl>

<dl>
<dd>

**filter_designators:** `typing.Optional[str]` 

Comma separated list of Object Designators to filter the request by. Can be combined with operators for more refined filtering.  Valid operators include:

EQUALS (ie. filterDesignators=12345),

NOT EQUALS (ie. filterDesignators=<>12345),

LIKE (ie. filterDesignators=*123)  The like value can fall anywhere in the objectDesignator string,

NOT LIKE(ie. filterDesignators=~*123)  The not like value can fall anywhere in the objectDesignator string,

GREATER THAN OR EQUAL TO (ie. filterDesignators=>=12345),

GREATER THAN (ie. filterDesignators=>12345),

LESS THAN OR EQUAL TO (ie. filterDesignators=<=12345),

LESS THAN (ie. filterDesignators=<12345),

IN (ie. filterDesignators=12345,67890,34567)  Comma separated list of objectDesignators,

BETWEEN (ie. filterDesignators=12345...67890) Lowest number in the range must be on the left.
    
</dd>
</dl>

<dl>
<dd>

**fields:** `typing.Optional[str]` — comma seperated list of fields to filter by. Only works with CDM and OCM topics
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

