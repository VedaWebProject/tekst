/**
 * This file was auto-generated by openapi-typescript.
 * Do not make direct changes to the file.
 */


export interface paths {
  "/admin": {
    /** Hello Admin */
    get: operations["helloAdmin"];
  };
  "/layers/plaintext/{layer_id}": {
    /**
     * Get Plaintext Layer 
     * @description Returns the data for a PlainText data layer
     */
    get: operations["getPlaintextLayer"];
  };
  "/layers/plaintext": {
    /**
     * Create Plaintext Layer 
     * @description Creates a PlainText data layer definition
     */
    post: operations["createPlaintextLayer"];
    /**
     * Update Plaintext Layer 
     * @description Updates the data for a PlainText data layer
     */
    patch: operations["updatePlaintextLayer"];
  };
  "/layers": {
    /** Get Layers */
    get: operations["getLayers"];
  };
  "/layers/template": {
    /** Get Layer Template */
    get: operations["getLayerTemplate"];
  };
  "/layers/{layer_id}": {
    /** Get Layer */
    get: operations["getLayer"];
  };
  "/nodes": {
    /** Get Nodes */
    get: operations["getNodes"];
    /** Create Node */
    post: operations["createNode"];
    /** Update Node */
    patch: operations["updateNode"];
  };
  "/nodes/{node_id}/children": {
    /** Get Children */
    get: operations["getChildren"];
  };
  "/nodes/{node_id}/next": {
    /** Get Next */
    get: operations["getNext"];
  };
  "/texts": {
    /** Get All Texts */
    get: operations["getAllTexts"];
    /** Create Text */
    post: operations["createText"];
    /** Update Text */
    patch: operations["updateText"];
  };
  "/texts/{text_id}": {
    /** Get Text By Id */
    get: operations["getTextById"];
  };
  "/uidata": {
    /**
     * Data the client needs to display in the UI 
     * @description Returns all UI data at once
     */
    get: operations["uidata"];
  };
  "/uidata/platform": {
    /**
     * Platform metadata 
     * @description Returns platform metadata, possibly customized for this platform instance.
     */
    get: operations["uidataPlatform"];
  };
  "/uidata/i18n": {
    /**
     * Help texts 
     * @description Returns server-managed translations.
     */
    get: operations["uidataI18n"];
  };
  "/uidata/help": {
    /**
     * Help texts 
     * @description Returns all help texts.
     */
    get: operations["uidataHelp"];
  };
  "/units/plaintext/{unit_id}": {
    /**
     * Get Plaintext Unit 
     * @description Returns the data for a PlainText data layer unit
     */
    get: operations["getPlaintextUnit"];
  };
  "/units/plaintext": {
    /**
     * Create Plaintext Unit 
     * @description Creates a PlainText data layer unit
     */
    post: operations["createPlaintextUnit"];
    /**
     * Update Plaintext Unit 
     * @description Updates the data for a PlainText data layer unit
     */
    patch: operations["updatePlaintextUnit"];
  };
}

export type webhooks = Record<string, never>;

export interface components {
  schemas: {
    /**
     * DeepLLinksConfig 
     * @description Base class for all TextRig models
     */
    DeepLLinksConfig: {
      /**
       * Enabled 
       * @description Enable/disable quick translation links to DeepL 
       * @default false
       */
      enabled?: boolean;
      /**
       * Sourcelanguage 
       * @description Source language 
       * @enum {string}
       */
      sourceLanguage?: "BG" | "CS" | "DA" | "DE" | "EL" | "EN" | "ES" | "ET" | "FI" | "FR" | "HU" | "ID" | "IT" | "JA" | "LT" | "LV" | "NL" | "PL" | "PT" | "RO" | "RU" | "SK" | "SL" | "SV" | "TR" | "UK" | "ZH";
      /**
       * Languages 
       * @description Target languages to display links for 
       * @default [
       *   "DE",
       *   "EN"
       * ]
       */
      languages?: ("BG" | "CS" | "DA" | "DE" | "EL" | "EN" | "ES" | "ET" | "FI" | "FR" | "HU" | "ID" | "IT" | "JA" | "LT" | "LV" | "NL" | "PL" | "PT" | "RO" | "RU" | "SK" | "SL" | "SV" | "TR" | "UK" | "ZH")[];
    };
    /** HTTPValidationError */
    HTTPValidationError: {
      /** Detail */
      detail?: (components["schemas"]["ValidationError"])[];
    };
    /**
     * Node 
     * @description A node in a text structure (e.g. chapter, paragraph, ...)
     */
    Node: {
      /**
       * Textslug 
       * @description Slug of the text this node belongs to
       */
      textSlug: string;
      /**
       * Parentid 
       * @description ID of parent node
       */
      parentId?: string;
      /**
       * Level 
       * @description Index of structure level this node is on
       */
      level: number;
      /**
       * Index 
       * @description Position among all text nodes on this level
       */
      index: number;
      /**
       * Label 
       * @description Label for identifying this text node
       */
      label: string;
      /**
       * Meta 
       * @description Arbitrary metadata
       */
      meta?: {
        [key: string]: (string | number | boolean | number) | undefined;
      };
    };
    /**
     * NodeRead 
     * @description An existing node read from the database
     */
    NodeRead: {
      /** Id */
      id: string;
      /**
       * Textslug 
       * @description Slug of the text this node belongs to
       */
      textSlug: string;
      /**
       * Parentid 
       * @description ID of parent node
       */
      parentId?: string;
      /**
       * Level 
       * @description Index of structure level this node is on
       */
      level: number;
      /**
       * Index 
       * @description Position among all text nodes on this level
       */
      index: number;
      /**
       * Label 
       * @description Label for identifying this text node
       */
      label: string;
      /**
       * Meta 
       * @description Arbitrary metadata
       */
      meta?: {
        [key: string]: (string | number | boolean | number) | undefined;
      };
    };
    /**
     * NodeUpdate 
     * @description An update to an existing node
     */
    NodeUpdate: {
      /** Id */
      id: string;
      /** Textslug */
      textSlug?: string;
      /** Parentid */
      parentId?: string;
      /** Level */
      level?: number;
      /** Index */
      index?: number;
      /** Label */
      label?: string;
      /** Meta */
      meta?: {
        [key: string]: (string | number | boolean | number) | undefined;
      };
    };
    /**
     * PlainTextLayer 
     * @description A data layer describing a set of data on a text
     */
    PlainTextLayer: {
      /**
       * Title 
       * @description Title of this layer
       */
      title: string;
      /**
       * Description 
       * @description Short, one-line description of this data layer
       */
      description?: string;
      /**
       * Textslug 
       * @description Slug of the text this layer belongs to
       */
      textSlug: string;
      /**
       * Level 
       * @description Text level this layer belongs to
       */
      level: number;
      /**
       * Layertype 
       * @description A string identifying one of the available layer types
       */
      layerType: string;
      /**
       * Public 
       * @description Publication status of this layer 
       * @default false
       */
      public?: boolean;
      /**
       * Meta 
       * @description Arbitrary metadata
       */
      meta?: {
        [key: string]: (string | number | boolean | number) | undefined;
      };
      /**
       * Config 
       * @default {}
       */
      config?: components["schemas"]["PlainTextLayerConfig"];
    };
    /**
     * PlainTextLayerConfig 
     * @description Base class for all TextRig models
     */
    PlainTextLayerConfig: {
      /**
       * Deepllinks 
       * @default {}
       */
      deeplLinks?: components["schemas"]["DeepLLinksConfig"];
    };
    /**
     * PlainTextLayerRead 
     * @description An existing data layer read from the database
     */
    PlainTextLayerRead: {
      /** Id */
      id: string;
      /**
       * Title 
       * @description Title of this layer
       */
      title: string;
      /**
       * Description 
       * @description Short, one-line description of this data layer
       */
      description?: string;
      /**
       * Textslug 
       * @description Slug of the text this layer belongs to
       */
      textSlug: string;
      /**
       * Level 
       * @description Text level this layer belongs to
       */
      level: number;
      /**
       * Layertype 
       * @description A string identifying one of the available layer types
       */
      layerType: string;
      /**
       * Public 
       * @description Publication status of this layer 
       * @default false
       */
      public?: boolean;
      /**
       * Meta 
       * @description Arbitrary metadata
       */
      meta?: {
        [key: string]: (string | number | boolean | number) | undefined;
      };
      /**
       * Config 
       * @default {}
       */
      config?: components["schemas"]["PlainTextLayerConfig"];
    };
    /**
     * PlainTextLayerUpdate 
     * @description An update to an existing data layer
     */
    PlainTextLayerUpdate: {
      /** Id */
      id: string;
      /** Title */
      title?: string;
      /** Description */
      description?: string;
      /** Textslug */
      textSlug?: string;
      /** Level */
      level?: number;
      /** Layertype */
      layerType?: string;
      /** Public */
      public?: boolean;
      /** Meta */
      meta?: {
        [key: string]: (string | number | boolean | number) | undefined;
      };
      config?: components["schemas"]["PlainTextLayerConfig"];
    };
    /**
     * PlainTextUnit 
     * @description A unit of a plaintext data layer
     */
    PlainTextUnit: {
      /**
       * Layerid 
       * @description Data layer ID
       */
      layerId: string;
      /**
       * Nodeid 
       * @description Parent text node ID
       */
      nodeId: string;
      /**
       * Meta 
       * @description Arbitrary metadata on this layer unit
       */
      meta?: {
        [key: string]: (string | number | boolean | number) | undefined;
      };
      /**
       * Text 
       * @description Text content of the plaintext unit
       */
      text?: string;
    };
    /**
     * PlainTextUnitRead 
     * @description A unit of a plaintext data layer
     */
    PlainTextUnitRead: {
      /** Id */
      id: string;
      /**
       * Layerid 
       * @description Data layer ID
       */
      layerId: string;
      /**
       * Nodeid 
       * @description Parent text node ID
       */
      nodeId: string;
      /**
       * Meta 
       * @description Arbitrary metadata on this layer unit
       */
      meta?: {
        [key: string]: (string | number | boolean | number) | undefined;
      };
      /**
       * Text 
       * @description Text content of the plaintext unit
       */
      text?: string;
    };
    /**
     * PlainTextUnitUpdate 
     * @description A unit of a plaintext data layer
     */
    PlainTextUnitUpdate: {
      /** Id */
      id: string;
      /** Layerid */
      layerId?: string;
      /** Nodeid */
      nodeId?: string;
      /** Meta */
      meta?: {
        [key: string]: (string | number | boolean | number) | undefined;
      };
      /** Text */
      text?: string;
    };
    /**
     * Text 
     * @description A text represented in TextRig
     */
    Text: {
      /**
       * Title 
       * @description Title of this text
       */
      title: string;
      /**
       * Slug 
       * @description A short identifier string for use in URLs and internal operations (will be generated automatically if missing)
       */
      slug?: string;
      /**
       * Subtitle 
       * @description Subtitle of this text
       */
      subtitle?: string;
      /** Levels */
      levels: (string)[];
      /**
       * Locdelim 
       * @description Delimiter for displaying text locations 
       * @default ,
       */
      locDelim?: string;
    };
    /**
     * TextRead 
     * @description An existing text read from the database
     */
    TextRead: {
      /** Id */
      id: string;
      /**
       * Title 
       * @description Title of this text
       */
      title: string;
      /**
       * Slug 
       * @description A short identifier string for use in URLs and internal operations (will be generated automatically if missing)
       */
      slug?: string;
      /**
       * Subtitle 
       * @description Subtitle of this text
       */
      subtitle?: string;
      /** Levels */
      levels: (string)[];
      /**
       * Locdelim 
       * @description Delimiter for displaying text locations 
       * @default ,
       */
      locDelim?: string;
    };
    /**
     * TextUpdate 
     * @description An update to an existing text
     */
    TextUpdate: {
      /** Id */
      id: string;
      /** Title */
      title?: string;
      /** Slug */
      slug?: string;
      /** Subtitle */
      subtitle?: string;
      /** Levels */
      levels?: (string)[];
      /** Locdelim */
      locDelim?: string;
    };
    /** ValidationError */
    ValidationError: {
      /** Location */
      loc: (string | number)[];
      /** Message */
      msg: string;
      /** Error Type */
      type: string;
    };
  };
  responses: never;
  parameters: never;
  requestBodies: never;
  headers: never;
  pathItems: never;
}

export type external = Record<string, never>;

export interface operations {

  helloAdmin: {
    /** Hello Admin */
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": Record<string, never>;
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
    };
  };
  getPlaintextLayer: {
    /**
     * Get Plaintext Layer 
     * @description Returns the data for a PlainText data layer
     */
    parameters: {
      path: {
        layer_id: string;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["PlainTextLayerRead"];
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  createPlaintextLayer: {
    /**
     * Create Plaintext Layer 
     * @description Creates a PlainText data layer definition
     */
    requestBody: {
      content: {
        "application/json": components["schemas"]["PlainTextLayer"];
      };
    };
    responses: {
      /** @description Successful Response */
      201: {
        content: {
          "application/json": components["schemas"]["PlainTextLayerRead"];
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  updatePlaintextLayer: {
    /**
     * Update Plaintext Layer 
     * @description Updates the data for a PlainText data layer
     */
    requestBody: {
      content: {
        "application/json": components["schemas"]["PlainTextLayerUpdate"];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["PlainTextLayerRead"];
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  getLayers: {
    /** Get Layers */
    parameters: {
      query: {
        text_slug: string;
        level?: number;
        layer_type?: string;
        limit?: number;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": (Record<string, never>)[];
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  getLayerTemplate: {
    /** Get Layer Template */
    parameters: {
      query: {
        layer_id: string;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": Record<string, never>;
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  getLayer: {
    /** Get Layer */
    parameters: {
      path: {
        layer_id: string;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": Record<string, never>;
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  getNodes: {
    /** Get Nodes */
    parameters: {
      query: {
        text_slug: string;
        level?: number;
        index?: number;
        parent_id?: string;
        limit?: number;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": (components["schemas"]["NodeRead"])[];
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  createNode: {
    /** Create Node */
    requestBody: {
      content: {
        "application/json": components["schemas"]["Node"];
      };
    };
    responses: {
      /** @description Successful Response */
      201: {
        content: {
          "application/json": components["schemas"]["NodeRead"];
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  updateNode: {
    /** Update Node */
    requestBody: {
      content: {
        "application/json": components["schemas"]["NodeUpdate"];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["NodeRead"];
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  getChildren: {
    /** Get Children */
    parameters: {
      query?: {
        limit?: number;
      };
      path: {
        node_id: string;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": (components["schemas"]["NodeRead"])[];
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  getNext: {
    /** Get Next */
    parameters: {
      path: {
        node_id: string;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["NodeRead"];
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  getAllTexts: {
    /** Get All Texts */
    parameters?: {
      query?: {
        limit?: number;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": (components["schemas"]["TextRead"])[];
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  createText: {
    /** Create Text */
    requestBody: {
      content: {
        "application/json": components["schemas"]["Text"];
      };
    };
    responses: {
      /** @description Successful Response */
      201: {
        content: {
          "application/json": components["schemas"]["TextRead"];
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  updateText: {
    /** Update Text */
    requestBody: {
      content: {
        "application/json": components["schemas"]["TextUpdate"];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["TextRead"];
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  getTextById: {
    /** Get Text By Id */
    parameters: {
      path: {
        text_id: string;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["TextRead"];
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  uidata: {
    /**
     * Data the client needs to display in the UI 
     * @description Returns all UI data at once
     */
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": Record<string, never>;
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
    };
  };
  uidataPlatform: {
    /**
     * Platform metadata 
     * @description Returns platform metadata, possibly customized for this platform instance.
     */
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": {
            [key: string]: string | undefined;
          };
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
    };
  };
  uidataI18n: {
    /**
     * Help texts 
     * @description Returns server-managed translations.
     */
    parameters?: {
      query?: {
        lang?: string;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": Record<string, never>;
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  uidataHelp: {
    /**
     * Help texts 
     * @description Returns all help texts.
     */
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": Record<string, never>;
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
    };
  };
  getPlaintextUnit: {
    /**
     * Get Plaintext Unit 
     * @description Returns the data for a PlainText data layer unit
     */
    parameters: {
      path: {
        unit_id: string;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["PlainTextUnitRead"];
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  createPlaintextUnit: {
    /**
     * Create Plaintext Unit 
     * @description Creates a PlainText data layer unit
     */
    requestBody: {
      content: {
        "application/json": components["schemas"]["PlainTextUnit"];
      };
    };
    responses: {
      /** @description Successful Response */
      201: {
        content: {
          "application/json": components["schemas"]["PlainTextUnitRead"];
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  updatePlaintextUnit: {
    /**
     * Update Plaintext Unit 
     * @description Updates the data for a PlainText data layer unit
     */
    requestBody: {
      content: {
        "application/json": components["schemas"]["PlainTextUnitUpdate"];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["PlainTextUnitRead"];
        };
      };
      /** @description Invalid Request */
      400: never;
      /** @description Not found */
      404: never;
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
}
