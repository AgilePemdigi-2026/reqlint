@backend @health
Feature: Pemeriksaan Kesehatan Sistem dan Info API (Backend)
  Sebagai engineer atau layanan frontend ReqLint
  Saya ingin memeriksa status kesiapan server, database, Redis, dan model SLM
  Agar saya dapat memastikan seluruh layanan ReqLint berjalan normal

  Scenario: Memeriksa endpoint Root API
    Given sistem ReqLint berjalan dan endpoint API siap
    When saya mengirim request GET ke "/"
    Then server merespons dengan status 200
    And field JSON "name" bernilai "ReqLint API"
    And field JSON "health" bernilai "/api/v1/health"

  Scenario: Memeriksa endpoint Healthcheck API v1
    Given sistem ReqLint berjalan dan endpoint API siap
    When saya mengirim request GET ke "/api/v1/health"
    Then server merespons dengan status 200
    And field JSON "status" bernilai "success"
    And field JSON "data.db" bernilai "up"
    And field JSON "data.redis" bernilai "up"

