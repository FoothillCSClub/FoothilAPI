# API

## Data overview
OwlAPI serves data directly from MyPortal. It parses and cleans the data in order to make it more usable. For now, only the most recent quarter's data is pulled from MyPortal. On [opencourse.dev](https://opencourse.dev), seat data is synced every 2 minutes with MyPortal.

### Class schema
| key          | description |
| ------------ | ----------- |
| `CRN`        | Course Number |
| `course`     | Course ID: `[F0*][ID][Section ID][WYH]` (see note below) |
| `desc`       | Short-form course description |
| `campus`     | Campus the section is held at |
| `days`       | Day(s) the section is held on (M, T, W, Th, F, S, U) |
| `instructor` | Professor for the section |
| `room`       | Room the section is held at |
| `time`       | Time for the section |
| `start`      | First date for the section |
| `end`        | Last date for the course |
| `units`      | Number of course units |
| `seats`      | Seats left in the course |
| `status`     | Status of the course (Online / Waitlist) |
| `wait_cap`   | Waitlist capacity |
| `wait_seats` | Waitlist slots left in the course |

#### Course variant format
| type   | flag |
| ------ | ---- |
| Online | `W` (Foothill) / `Z` (De Anza) |
| Hybrid | `Y` |
| Honors | `H` |

## Endpoints
#### Campus selector
Before any of the endpoints below, you must select which campus' data you'd like the query. Before the endpoint type `/fh` or `/da` for Foothill and De Anza respectively.

Alternatively, if either campus' data cannot be accessed, a debug campus has been put into production. Use the
campus selector `test` to grab this older copy of Foothill data.

<!-- playground:api ["GET", "/da/list", "?dept=CIS", "2C, 49, 30A, 80A, 18, 21B, 50E, 3A, 22A, 50C, 50A, 20A, 2A, 1B, 1A, 81A, 53A, 82A, 30B, 63A, 21A, 53B, 1C, 2B, 10, 31A, 60A"] -->

### Get single
`GET /single` handles a single request to get a whole department or a whole course listing from the database
It expects a mandatory query parameter `dept` and an optionally `course`.

<!-- playground:api ["GET", "/fh/single", "?dept=CS", [
  {
    "1B": {
      "20339": [
        {
          "CRN": "20339",
          "campus": "FH",
          "course": "C S F001B01Z",
          "days": "TTh",
          "desc": "INTERM SOFTWARE DESIGN IN JAVA",
          "end": "12/11/2020",
          "instructor": "Mansouri Samani",
          "room": "ONLINE",
          "seats": "30",
          "start": "09/21/2020",
          "status": "Open",
          "time": "06:00 PM-07:50 PM",
          "units": "4.50",
          "wait_cap": "10",
          "wait_seats": "10"
        },
        {
          "...": "..."
        }
      ],
      "20463": ["..."]
    },
    "1C": {
      "...": "..."
    }
  }
]] -->

<!-- playground:api ["GET", "/fh/single", "?dept=CS&course=2A", {
  "10116": [
    {
      "CRN": "10116",
      "campus": "FH",
      "course": "C S F002A01W",
      "days": "TBA",
      "desc": "OBJ-ORIENT PROG METHOD IN C++",
      "end": "08/12/2018",
      "instructor": "Venkataraman",
      "room": "ONLINE",
      "seats": "34",
      "start": "07/02/2018",
      "status": "Open",
      "time": "TBA",
      "units": "4.50",
      "wait_cap": "10",
      "wait_seats": "10"
    },
    { "...": "..." }
  ]
}] -->

`/single` returns a JSON format with the keys as the CRN for the course, and the values as a list. The list is necessary to account for hybrid classes or classes with labs, that have two or more listings per CRN.

You can view an example of the `/single` route [here](/examples/single/).


### Get batch
`POST /batch` handles a batch request to get many departments or many sections from the database.
This batch request is meant to simulate hitting the api route with this data N times.
It expects a mandatory list of objects containing keys `dept` and `course`.

<!-- playground:api ["POST", "/fh/batch", {
  "courses": [
    { "dept": "CS", "course": "2A" },
    { "dept": "MATH", "course": "1A" },
    { "dept": "ENGL", "course": "1A" }
  ]
}] -->

`/batch` returns a JSON format with the initial key as `courses` and a value containing a list of courses. The courses are formatted in the same way as found in the `/single` response.

You can view an example of the `/batch` route [here](/examples/batch/).


### Filters
Additionally, in the `POST /batch` body you can specify any number of filters to narrow the results. Add the filter key to the post body and then apply the appropriate filter. Multiple options can be selected by changing the value from a `0` to a `1`.
Be careful because too many filters may result in zero sections returned from the database. Also, even if 2 out of 3 courses are valid, one invalid will return `404`.

#### Filter by status
Filter by the availability of a course (Open, Waitlist, Full). The example below shows how you can filter only `open` and `waitlist` sections.

<!-- playground:api ["POST", "/fh/batch", {
  "courses": [
    { "dept": "CS", "course": "2A" }
  ],
  "filters": {
    "status": {
      "open": 1,
      "waitlist": 1,
      "full": 0
    }
  }
}] -->

#### Filter by type
Filter by the format of the course (In Person, Online, Hybrid). The example below shows how you can filter only `online` and `hybrid` sections.

<!-- playground:api ["POST", "/fh/batch", {
  "courses": [
    { "dept": "CS", "course": "2A" }
  ],
  "filters": {
    "types": {
      "standard": 0,
      "online": 1,
      "hybrid": 1
    }
  }
}] -->

#### Filter by days
Filter by the days the course should be limited to (M, T, W, Th, F, S, U). The example below shows how you can filter only `M` and `W` sections.

<!-- playground:api ["POST", "/fh/batch", {
  "courses": [
    { "dept": "CS", "course": "2A" }
  ],
  "filters": {
    "days": { "M": 1, "T": 0, "W": 1, "Th": 0, "F": 0, "S": 0, "U": 0 }
  }
}] -->


#### Filter by time
Filter by a specified time interval (7:30 AM - 12:00 PM). The example below shows how you can filter only morning sections.

<!-- playground:api ["POST", "/fh/batch", {
  "courses": [
    { "dept": "CS", "course": "2A" }
  ],
  "filters": {
    "time": {
      "start": "7:30 AM",
      "end": "12:00 PM"
    }
  }
}] -->


### List
`GET /list` handles a single request to list department or course keys from the database
It takes an optional query parameter `dept` which is first checked for existence and then returns the dept keys.

<!-- playground:api ["GET", "/fh/list", "", "IDS, CHLD, ALTW, ANTH, SPAN, CRWR, DH, NCLA, POLI, CHEM, CNSL, GIST, MTEC, ASTR, PHOT, ITRN, DMS, AHS, EMTP, ATHL, APEL, HIST, HORT, GEOG, SPED, ALCB, RT, MDIA, ENGR, THTR, NCSV, NCBS, ACTG, NCEL, KINS, DANC, HUMN, DA, JAPN, CRLP, VITI, BIOL, BUSI, PSE, ECON, RSPT, ART, NCBH, PHT, LA, CS, LINC, MUS, EMS, PHED, ENGL, VT, HLTH, APPT, MATH, COMM, NCP, GID, LIBR, APSM, PHDA, PHIL, WMN, NANO, PSYC, ESLL, SOC, APIW, PHYS"] -->

<!-- playground:api ["GET", "/fh/list", "?dept=CS", "2C, 49, 30A, 80A, 18, 21B, 50E, 3A, 22A, 50C, 50A, 20A, 2A, 1B, 1A, 81A, 53A, 82A, 30B, 63A, 21A, 53B, 1C, 2B, 10, 31A, 60A"] -->


### URLs
`GET /urls` returns a tree of all departments, their courses, and the courses' endpoints to hit.

<!-- playground:api ["GET", "/fh/urls", "", {
  "CS": [
    {
      "2A": {
        "course": "2A",
        "dept": "CS"
      },
      "2B": {
        "course": "2B",
        "dept": "CS"
      },
      "2C": {
        "course": "2C",
        "dept": "CS"
      },
      "...": "..."
    }
  ],
  "MATH": [{ "...": "..." }]
}] -->
